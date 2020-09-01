from flask import request, jsonify,session,g
from ..models import Article, User, Comment,ArticleImg
import time
from ..func.token_auth import auth as http_auth
from . import main
from .. import db


@main.route("/")
def admin():
    return jsonify({'msg': '欢迎访问博客主页'})


# 显示所有文章
@main.route('/arc_lists', methods=["GET", "POST"])
def get_articles():
    if request.method == "POST":
        # 查询指定编号的文章
        aid = request.get_json().get("aid")
        arc_data = db.session.query(Article.id, Article.title, Article.content, Article.article_type,
                                    Article.article_dianzan, Article.addtime, User.name,).join(User).filter(Article.id == aid).all()
        # 获取文章所属评论信息
        comment = db.session.query(Comment.id, Comment.comment, Comment.addtime, User.name).join(User).filter(
            Comment.article_id == aid).all()
        # print(comment)
        return jsonify({"code": 200, "msg": "查询博客文章成功", "arc_data": arc_data, "comment": comment, "comment_count": len(comment)})
    # 获取所有文章信息
    # page=int(request.get_json().get("page"))
    page=request.args['page']
    page=int(page)
    per_page = int(request.args.get('per_page', 10))
    arc_data = db.session.query(Article.id, Article.title, Article.content, Article.article_type,
                                Article.article_dianzan, Article.addtime, User.name).join(User).order_by(Article.addtime).paginate(page, per_page, error_out=False)


    arc_data = {
        "current_page" : arc_data.page,
        "pages": arc_data.pages,  # 总页数
        "arc_nums": arc_data.total,  # 数据的总条数
         "arc_info":arc_data.items
        #   {
        #     "aid":arc_data.items[0],
        #     "title":arc_data.items[1],
        #     "content":arc_data.items[2],
        #     "article_type":arc_data.items[3],
        #     "article_dianzan":arc_data.items[4],
        #     "addtime":arc_data.items[5],
        #     "auhtor":arc_data.items[6],
        #  }   # 数据
    }
    # 获取文章的评论数量
    comment_count = db.session.query(Comment).filter(
        Comment.article_id == Article.id).count()
    # print(comment_count)
    # return jsonify({"code":200,"msg":"查询博客文章成功","arc_data":arc_data})
    return jsonify(code=200, msg="查询博客文章成功", arc_data=arc_data)


# 文章详情页
@main.route("/articles/<int:id>", methods=["GET"])
def show_article(id):
    try:
        article = db.session.query(Article.id,Article.title,Article.content,Article.addtime,Article.article_dianzan,Article.article_type,User.name).filter_by(id=id).first()
        print(article)
    except:
        return jsonify({"code": "400", "msg": "获取文章失败"})
    try:
        comments = db.session.query(
            Comment.id, Comment.user_id, Comment.comment, Comment.addtime).filter_by(article_id=id).all()
    except:
        return jsonify({"code": "400", "msg": "获取评论信息失败"})
    return jsonify({"msg": "获取博客，评论信息成功", "data": {"articles": article, "cimments": comments}})


# 发表文章
@main.route("articles", methods=["POST"])
@http_auth.login_required
def write_article():
    user_id=g.user_id
    arc_data = request.get_json()
    title = arc_data.get("title")
    content = arc_data.get("content")
    article_type = arc_data.get("arc_type")
    arc_img = arc_data.get("arc_img")
    #c_time=time.strftime('%Y-%m-%d %H:%M:%S' , time.localtime(time.time()))
    article = Article(
        user_id=user_id,
        title=title,
        content=content,
        article_type=article_type,
        addtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    try:
        db.session.add(article)
        db.session.commit()
    except:
        db.rollback()
        return jsonify({"msg": "数据库错误"})
    try:
        article=db.session.query(Article.id).filter(Article.title==title).first()
        print(article.id)
    except:
         return jsonify({"msg": "数据库错误"})
    article_img=ArticleImg(
        img_path=arc_img,
        article_id=article.id,
        addtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    )
    try:
        db.session.add(article_img)
        db.session.commit()
        return jsonify({"msg": "数据库保存文章成功"})
    except:
        db.rollback()
        return jsonify({"msg": "数据库错误"})


# 用户获取自己发表的文章
@main.route("/users/articles", methods=["POST"])
@http_auth.login_required
def get_own_article():
    id =g.user_id
    if not id:
        return jsonify({'msg': '此api不能获取不是自己发表的博客'})  # ？？？？？？？？？？
    page=request.args['page']
    page=int(page)
    per_page = int(request.args.get('per_page', 5))
    try:
        username = User.query.filter_by(id=id).first()
        # articles 是[object,..]结构，需要序列化为json字符串结构
        
        arc_data = db.session.query(Article.id, Article.title, Article.content, Article.article_type,
                                Article.article_dianzan, Article.addtime, User.name).join(User).filter(Article.user_id==id).all()
    except:
        return jsonify({"code": 5001, "msg": "查询数据库失败"})
    arc_data = {
        "current_page" : arc_data.page,
        "pages": arc_data.pages,  # 总页数
        "arc_nums": arc_data.total,  # 数据的总条数
         "arc_info": arc_data.items   # 数据
    }
    return jsonify({"code": 200, "msg": "查询博客文章成功", "arc_data": arc_data})


# 显示当前用户发表文章详情??????
@main.route("/users/<uid>articles/<int:aid>", methods=["GET"])
@http_auth.login_required
def show__user_article_detial(uid, aid):
    if uid != session.get("user_id"):
        return jsonify({'msg': '非法访问，此用户id非作者id'})
    user_arc_data = db.session.query(User.name, Article.title, Article.content, Article.addtime).filter_by(
        User.id == uid, Article.id == aid).all()
    return jsonify({"msg": "获取文章详情成功", "article": user_arc_data})


# 发表评论
@main.route("/comments", methods=["POST"])
@http_auth.login_required
def write_comment():
    comment_data = request.get_json()
    if not comment_data:
        return jsonify(code=1001, msg="参数错误")
    article_id = comment_data.get("aid")
    comment = comment_data.get("comment_data")
    user_id = g.user_id
    if not user_id:
        return jsonify({"status": "Unauthorized", "code": 401, "msg": "请求未包含认证信息", "data": ""})
    comment = Comment(
        user_id=user_id,
        comment=comment,
        article_id=article_id,
        addtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    try:
        db.session.add(comment)
        db.session.commit()
        # return jsonify({"status": "Created", "code": 201, "msg": "请求成功完成并创建了一个新资源", "data": ""})
    except:
        db.rollback()
        return jsonify({"status": "DBerror", "code": 5001, "msg": "数据库错误", "data": ""})
    try:
        comment = db.session.query(
            Comment.id, Comment.user_id, Comment.comment, Comment.addtime, User.name).join(User).filter(Comment.article_id == article_id).order_by(Comment.addtime.desc()).all()
    except:
        return jsonify({"status": "DBerror", "code": 5002, "msg": "数据库查询错误", "data": ""})
    return jsonify({"status": "Created", "code": 201, "msg": "请求成功完成并创建了一个新资源", "comment": comment})


# 展示自己发表的全部评论
@main.route("/users/comments", methods=["POST"])
@http_auth.login_required
def show_comments():
    user_id = g.user_id
    if not user_id:
        return jsonify({"status": "Unauthorized", "code": 401, "msg": "请求未包含认证信息", "data": ""})
    try:
        comments = db.session.query(Comment.id, Comment.comment, Comment.addtime).filter(
            Comment.user_id == user_id).all()
        return jsonify({"status": "ok", "code": 200, "msg": "请求成功", "com_data": comments})
    except:
        return jsonify({"status": "db_query_error", "code": 5002, "msg": "数据库查询错误", "data": ""})

 # 获取某个文章的全部评论


@main.route("/articles/<int:aid>/comments", methods=["GET"])
def show_article_comments(aid):
    try:
        arc_comments = db.session.query(Comment.comment, Comment.addtime, User.name).filter(
            Comment.article_id == aid, User.id == Comment.id).all()
        return jsonify({"status": "ok", "code": 200, "msg": "请求成功", "data": arc_comments})
    except:
        return jsonify({"status": "db_query_error", "code": 5002, "msg": "数据库查询错误", "data": ""})
