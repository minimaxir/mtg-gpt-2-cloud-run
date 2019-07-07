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

    card_name = params.get('card_name', '')[:30].lower().strip()
    card_type = params.get('card_type', '')
    card_mana = params.get('card_mana', '')

    text = "|"
    if card_name != '':
        text += '1' + card_name
    if card_type != '':
        text += '5' + card_type
    if card_mana != '':
        text += '3' + card_mana

    length = MIN_LENGTH

    while '\n' not in text and length <= MAX_LENGTH:
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

    pattern = '(.*)(?:\n)'

    trunc_text = re.search(pattern, text)

    return UJSONResponse({'text': trunc_text.group(1)},
                         headers=response_header)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
