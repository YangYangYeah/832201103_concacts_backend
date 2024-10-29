from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用跨域资源共享

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    special_care = db.Column(db.Boolean, default=False)
    blacklist = db.Column(db.Boolean, default=False)

# 获取联系人列表（不包含黑名单中的联系人）
@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.filter_by(blacklist=False).all()
    contacts_sorted = sorted(contacts, key=lambda x: x.special_care, reverse=True)
    contacts_list = [{
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone,
        'student_id': contact.student_id,
        'special_care': contact.special_care,
        'blacklist': contact.blacklist
    } for contact in contacts_sorted]
    return jsonify(contacts_list)

# 根路径路由，返回所有联系人（特别关心的联系人置顶，黑名单的联系人被过滤）
@app.route('/', methods=['GET'])
def index():
    contacts = Contact.query.filter_by(blacklist=False).all()
    contacts_sorted = sorted(contacts, key=lambda x: x.special_care, reverse=True)
    contacts_list = [{
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone,
        'student_id': contact.student_id,
        'special_care': contact.special_care,
        'blacklist': contact.blacklist
    } for contact in contacts_sorted]
    return jsonify(contacts_list)

# 添加联系人
@app.route('/add_contact', methods=['POST'])
def add_contact():
    data = request.json
    new_contact = Contact(
        name=data['name'],
        phone=data['phone'],
        student_id=data['student_id']
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"message": "Contact added successfully!"}), 201

# 删除联系人
@app.route('/delete_contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contact deleted successfully!"}), 200

# 切换特别关心状态
@app.route('/toggle_special_care/<int:id>', methods=['POST'])
def toggle_special_care(id):
    contact = Contact.query.get_or_404(id)
    contact.special_care = not contact.special_care
    db.session.commit()
    return jsonify({"message": f"Contact special care status toggled to {contact.special_care}"}), 200

# 获取黑名单中的联系人列表
@app.route('/blacklist_contacts', methods=['GET'])
def blacklist_contacts():
    contacts = Contact.query.filter_by(blacklist=True).all()
    blacklist_list = [{
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone,
        'student_id': contact.student_id,
        'special_care': contact.special_care,
        'blacklist': contact.blacklist
    } for contact in contacts]
    return jsonify(blacklist_list)

# 切换黑名单状态
@app.route('/toggle_blacklist/<int:id>', methods=['POST'])
def toggle_blacklist(id):
    contact = Contact.query.get_or_404(id)
    contact.blacklist = not contact.blacklist
    db.session.commit()
    return jsonify({"message": f"Contact blacklist status toggled to {contact.blacklist}"}), 200

# 更新联系人信息的路由
@app.route('/update_contact/<int:id>', methods=['PUT'])
def update_contact(id):
    data = request.json
    contact = Contact.query.get_or_404(id)

    contact.name = data.get('name', contact.name)
    contact.phone = data.get('phone', contact.phone)
    contact.student_id = data.get('student_id', contact.student_id)

    db.session.commit()
    return jsonify({"message": "Contact updated successfully!"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 在应用上下文中创建所有表
    app.run(host='0.0.0.0', port=5000, debug=True)
