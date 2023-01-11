from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import config
app = Flask(__name__)


def f(x):
    result = {}
    result['id'] = x.id
    result['title'] = x.title
    result['content'] = x.content
    result['status'] = x.status
    result['time'] = x.time
    result['ddl'] = x.ddl
    return result


with app.app_context():

    app.config.from_object(config)
    db = SQLAlchemy(app)  # 实例化的数据库

    # 建表
    class Todo_List(db.Model):
        __tablename__ = 'Todo_List'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        title = db.Column(db.VARCHAR(200), nullable=False)
        content = db.Column(db.VARCHAR(200), nullable=False)
        status = db.Column(db.Enum('已完成', '待办'), nullable=False)
        time = db.Column(db.TIMESTAMP(True), nullable=True)
        ddl = db.Column(db.TIMESTAMP(True), nullable=True)
    db.create_all()

    # 添加一条新的待办事项
    @app.route('/todolist/adding/one', methods=['POST'])
    def adding_one():
        try:
            gj = request.get_json()
            a = Todo_List(title=gj.get('title'),
                          content=gj.get('content'),
                          status=gj.get('status'),
                          time=gj.get('time'),
                          ddl=gj.get('ddl'))
            db.session.add(a)
            db.session.commit()
            return jsonify(code=200, msg='success')
        except:
            return jsonify(code=400, msg='Bad Request')

    # 将一条待办事项设置为已完成
    @app.route('/todolist/updating/completed/one', methods=['POST'])
    def updating_completed_one():
        try:
            gj = request.get_json()
            up = Todo_List.query.filter(Todo_List.id == gj.get('id'))
            up.update({'status': '已完成'})
            db.session.commit()
            return jsonify(code=200, msg='success')
        except:
            return jsonify(code=400, msg='Bad Request')

    # 将所有待办事项设置为已完成
    @app.route('/todolist/updating/completed/all', methods=['GET'])
    def update_completed_all():
        up = Todo_List.query.filter(Todo_List.id > 0)
        up.update({'status': '已完成'})
        db.session.commit()
        return jsonify(code=200, msg='success')

    # 将一条已完成事项设置为待办
    @app.route('/todolist/updating/waited/one', methods=['POST'])
    def update_waited_one():
        try:
            gj = request.get_json()
            up = Todo_List.query.filter(Todo_List.id == gj.get('id'))
            up.update({'status': '待办'})
            db.session.commit()
            return jsonify(code=200, msg='success')
        except:
            return jsonify(code=400, msg='Bad Request')

    # 将所有已完成事项设置为待办
    @app.route('/todolist/updating/waited/all', methods=['GET'])
    def update_waited_all():
        up = Todo_List.query.filter(Todo_List.id > 0)
        up.update({'status': '待办'})
        db.session.commit()
        return jsonify(code=200, msg='success')

    # 查看所有已完成事项
    @app.route('/todolist/searching/completed/<int:offset>/<int:limit>', methods=['GET'])
    def searching_completed(offset, limit):
        se = Todo_List.query.filter(Todo_List.status == '已完成').offset(offset).limit(limit)
        jsondata = []
        for i in se:
            result = f(i)
            jsondata.append(result)
        db.session.commit()
        return jsonify(code=200, msg='success', data=jsondata)

    # 查看所有待办事项
    @app.route('/todolist/searching/waited/<int:offset>/<int:limit>', methods=['GET'])
    def searching_waited(offset, limit):
        se = Todo_List.query.filter(Todo_List.status == '待办').offset(offset).limit(limit)
        jsondata = []
        for i in se:
            result = f(i)
            jsondata.append(result)
        db.session.commit()
        return jsonify(code=200, msg='success', data=jsondata)

    # 查看所有事项
    @app.route('/todolist/searching/all/<int:offset>/<int:limit>', methods=['GET'])
    def searching_all(offset, limit):
        se = Todo_List.query.offset(offset).limit(limit).all()
        jsondata = []
        for i in se:
            result = f(i)
            jsondata.append(result)
        db.session.commit()
        return jsonify(code=200, msg='success', data=jsondata)

    # 输入关键字查询事项
    @app.route('/todolist/searching/kw/<int:offset>/<int:limit>', methods=['POST'])
    def searching_kw(offset, limit):
        try:
            gj = request.get_json().get('kw')
            al = Todo_List.query.all()
            jsondata = []
            for i in al:
                if gj in i.title or gj in i.content:
                    result = f(i)
                    jsondata.append(result)
            db.session.commit()
            jsondata = jsondata[offset: offset+limit]
            return jsonify(code=200, msg='success', data=jsondata)
        except:
            return jsonify(code=400, msg='Bad Request')

    # 通过id查询事项
    @app.route('/todolist/searching/id', methods=['POST'])
    def searching_id():
        try:
            gj = request.get_json()
            se = Todo_List.query.filter(Todo_List.id == gj.get('id'))[0]
            db.session.commit()
            jsondata = {
                'id': se.id,
                'title': se.title,
                'content': se.content,
                'time': se.time,
                'ddl': se.ddl
            }
            return jsonify(code=200, msg='success', data=jsondata)
        except:
            return jsonify(code=400, msg='Bad Request')

    # 删除一条事项
    @app.route('/todolist/deleting/one', methods=['POST'])
    def deleting_one():
        try:
            gj = request.get_json()
            Todo_List.query.filter(Todo_List.id == gj.get('id')).delete()
            db.session.commit()
            return jsonify(code=200, msg='success')
        except:
            return jsonify(code=400, msg='Bad Request')

    # 删除所有已完成事项
    @app.route('/todolist/deleting/completed', methods=['GET'])
    def deleting_completed():
        Todo_List.query.filter(Todo_List.status == '已完成').delete()
        db.session.commit()
        return jsonify(code=200, msg='success')

    # 删除所有待办事项
    @app.route('/todolist/deleting/waited', methods=['GET'])
    def deleting_waited():
        Todo_List.query.filter(Todo_List.status == '待办').delete()
        db.session.commit()
        return jsonify(code=200, msg='success')

    # 删除所有事项
    @app.route('/todolist/deleting/all', methods=['GET'])
    def deleting_all():
        Todo_List.query.filter(Todo_List.id > 0).delete()
        db.session.commit()
        return jsonify(code=200, msg='success')

app.run()

