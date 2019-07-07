from starlette.applications import Starlette
from starlette.responses import UJSONResponse
import gpt_2_simple as gpt2
import tensorflow as tf
import uvicorn
import os
import re


MIN_LENGTH = 50
MAX_LENGTH = 200
STEP_LENGTH = 50

INVALID_SUBREDDITS = set([
    "me_irl",
    "2meirl4meirl",
    "anime_irl",
    "furry_irl",
    "cursedimages",
    "meirl",
    "hmmm",
    "ooer"
])

app = Starlette(debug=False)

sess = gpt2.start_tf_sess(threads=1)
gpt2.load_gpt2(sess)

# Needed to avoid cross-domain issues
response_header = {
    'Access-Control-Allow-Origin': '*'
}

generate_count = 0


@app.route('/', methods=['GET', 'POST', 'HEAD'])
async def homepage(request):
    global generate_count
    global sess

    if request.method == 'GET':
        params = request.query_params
    elif request.method == 'POST':
        params = await request.json()
    elif request.method == 'HEAD':
        return UJSONResponse({'text': ''},
                             headers=response_header)

    subreddit = params.get('subreddit', '').lower().strip()

    if subreddit == '':
        subreddit = 'askreddit'

    if subreddit in INVALID_SUBREDDITS:
        return UJSONResponse({'text': '<span style="font-size: 2em">ಠ_ಠ</span>'},
                             headers=response_header)

    keywords = " ".join([v.replace(' ', '-').strip() for k, v in params.items()
                         if 'key' in k and v != ''])

    prepend = "<|startoftext|>~`{}~^{}~@".format(subreddit, keywords)
    text = prepend + params.get('prefix', '')[:100]

    length = MIN_LENGTH

    while '<|endoftext|>' not in text and length <= MAX_LENGTH:
        text = gpt2.generate(sess,
                             length=STEP_LENGTH,
                             temperature=0.7,
                             top_k=40,
                             prefix=text,
                             include_prefix=True,
                             return_as_list=True
                             )[0]
        length += STEP_LENGTH

        generate_count += 1
        if generate_count == 8:
            # Reload model to prevent Graph/Session from going OOM
            tf.reset_default_graph()
            sess.close()
            sess = gpt2.start_tf_sess(threads=1)
            gpt2.load_gpt2(sess)
            generate_count = 0

    prepend_esc = re.escape(prepend)
    eot_esc = re.escape('<|endoftext|>')

    if '<|endoftext|>' not in text:
        pattern = '(?:{})(.*)'.format(prepend_esc)
    else:
        pattern = '(?:{})(.*)(?:{})'.format(prepend_esc, eot_esc)

    trunc_text = re.search(pattern, text)

    return UJSONResponse({'text': trunc_text.group(1)},
                         headers=response_header)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
