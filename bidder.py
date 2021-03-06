from flask import jsonify
from flask import request
from flask import make_response

import ad
from app import app
from app import statsd_client
import bid


@app.route('/bid', methods=['POST'])
@statsd_client.timer('bidder.bid')
def bid_():
    bid_request = request.json
    bid_id, bid_response, ad_ids = bid.generate_response(bid_request)
    [ad.incr_report(ad_id, 'bids', 1) for ad_id in ad_ids]
    bid.store_request(bid_id, bid_request)
    bid.store_response(bid_id, bid_response)
    if bid_response:
        return jsonify(bid_response)
    else:
        return make_response('', 204)


@app.route('/win_notice', methods=['GET'])
@statsd_client.timer('bidder.win_notice')
def win_notice():
    bid.persist_request(request.args['bid_id'])
    ad.incr_report(request.args['ad_id'], 'wons', 1)
    ad.incr_report(request.args['ad_id'], 'spend',
                   float(request.args['price'])/1000.0)
    return make_response('', 200)

