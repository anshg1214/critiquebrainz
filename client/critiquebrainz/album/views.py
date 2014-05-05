from flask import Blueprint, render_template, request
from flask.ext.login import current_user

from critiquebrainz.api import api
from critiquebrainz import musicbrainz


bp = Blueprint('album', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def release_group_entity_handler(id):
    album = musicbrainz.album_details(id)
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    my_count, my_reviews = api.get_reviews(release_group=id, user_id=current_user.me['id'])
    if my_count != 0:
        my_review = my_reviews[0]
    else:
        my_review = None
    count, reviews = api.get_reviews(release_group=id, sort='created',
                                     limit=limit, offset=offset, inc=['user'])
    return render_template('album.html', id=id, album=album, reviews=reviews, my_review=my_review,
                           limit=limit, offset=offset, count=count)
