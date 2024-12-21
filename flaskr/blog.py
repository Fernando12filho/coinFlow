import sqlite3
import os
from flask import (
    Blueprint, jsonify
)
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/api/blog-posts', methods=['GET'])
def get_blog_posts():
    conn = get_db()
    posts = conn.execute('SELECT * FROM blog_posts').fetchall()
    conn.close()
    return jsonify([dict(post) for post in posts])

@bp.route('/api/blog-posts/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify(dict(post))

