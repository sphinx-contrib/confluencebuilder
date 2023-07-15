httpdomain
==========

.. http:get:: /users/(int:user_id)/posts/(tag)

    The posts tagged with `tag` that the user (`user_id`) wrote.

    **Example request**:

    .. sourcecode:: http

        GET /users/123/posts/web HTTP/1.1
        Host: example.com
        Accept: application/json, text/javascript

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        [
            {
                "post_id": 12345,
                "author_id": 123,
                "tags": ["server", "web"],
                "subject": "I tried Nginx"
            },
            {
                "post_id": 12346,
                "author_id": 123,
                "tags": ["html5", "standards", "web"],
                "subject": "We go to HTML 5"
            }
        ]

    :query sort: one of ``hit``, ``created-at``
    :query offset: offset number. default is 0
    :query limit: limit number. default is 30
    :reqheader Accept: the response content type depends on
                       :mailheader:`Accept` header
    :reqheader Authorization: optional OAuth token to authenticate
    :resheader Content-Type: this depends on :mailheader:`Accept`
                             header of request
    :statuscode 200: no error
    :statuscode 404: there's no user


.. http:post:: /posts/(int:post_id)

    Replies a comment to the post.

    :param post_id: post's unique id
    :type post_id: int
    :form email: author email address
    :form body: comment body
    :reqheader Accept: the response content type depends on
                       :mailheader:`Accept` header
    :reqheader Authorization: optional OAuth token to authenticate
    :resheader Content-Type: this depends on :mailheader:`Accept`
                             header of request
    :status 302: and then redirects to :http:get:`/posts/(int:post_id)`
    :status 400: when form parameters are missing

.. http:get:: /posts/(int:post_id)

    Fetches the post

    (...)
