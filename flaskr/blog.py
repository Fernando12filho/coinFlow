import sqlite3
import os
from flask import (
    Blueprint, jsonify
)
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/api/blog-posts', methods=['GET'])
def get_blog_posts():
    """
    Fetch all blog posts.
    Uses Flask's g object for connection management.
    """
    try:
        db = get_db()
        posts = db.execute('SELECT * FROM blog_posts').fetchall()
        # Don't close - Flask's g object handles it automatically
        return jsonify([dict(post) for post in posts])
    except Exception as e:
        print(f"Error fetching blog posts: {str(e)}")
        return jsonify({'error': 'Failed to fetch blog posts'}), 500

@bp.route('/api/blog-posts/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    """
    Fetch a single blog post by ID.
    Uses parameterized query to prevent SQL injection.
    """
    try:
        db = get_db()
        post = db.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,)).fetchone()
        # Don't close - Flask's g object handles it automatically
        
        if post is None:
            return jsonify({'error': 'Post not found'}), 404
            
        return jsonify(dict(post))
    except Exception as e:
        print(f"Error fetching blog post {post_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch blog post'}), 500

