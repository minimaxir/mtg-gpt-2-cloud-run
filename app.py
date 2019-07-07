from starlette.applications import Starlette
from starlette.responses import UJSONResponse
from collections import Counter
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


async def encode_mana(card_mana):

    # extract out mana patterns in brackets.
    hybrid_pattern = r'(?:\{)(.*?)(?:\})'
    hybrid_costs = ''.join(re.findall(hybrid_pattern, card_mana))

    # extract colorless number
    colorless_pattern = r'(\d+)'
    colorless_number = re.findall(colorless_pattern, card_mana)
    if len(colorless_number) > 0:
        colorless_costs = ''.join(['^' * int(colorless_number[0])])
    else:
        colorless_costs = ''

    # get normal mana symbols
    normal_costs = re.sub(r'(\{.*?\})', '', card_mana)
    normal_costs = re.sub(r'(\d+)', '', normal_costs)
    normal_costs = ''.join(x + x for x in normal_costs)

    return '{' + colorless_costs + normal_costs + hybrid_costs + '}'


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

    text = "<|startoftext|>|"
    if card_name != '':
        text += '1' + card_name + "|"
    if card_type != '':
        text += '5' + card_type + "|"
    if card_mana != '':
        try:
            mana_enc = encode_mana(card_mana)
        except:
            return UJSONResponse({'text': 'The mana cost was entered incorrectly!'},
                                 headers=response_header)
        text += '3' + card_mana + "|"

    length = MIN_LENGTH
    good_text = False
    while not good_text:
        while '<|endoftext|>' not in text and length <= MAX_LENGTH:
            text = gpt2.generate(sess,
                                 length=STEP_LENGTH,
                                 temperature=1.0,
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

        prepend_esc = re.escape('<|startoftext|>')
        eot_esc = re.escape('<|endoftext|>')
        pattern = '(?:{})(.*)(?:{})'.format(prepend_esc, eot_esc)
        trunc_text = re.search(pattern, text)

        # ensure there is only one of each section in the generated card
        counts = Counter(trunc_text)
        section_ids = ['0', '1', '3', '4', '5', '6', '7', '8', '9']
        if all([counts[x] == 1 for x in section_ids]):
            good_text = True

    return UJSONResponse({'text': trunc_text.group(1)},
                         headers=response_header)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
