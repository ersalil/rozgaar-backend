from flask import Flask, flash, request, redirect, send_from_directory
from flask_mysqldb import MySQL
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import json
from flask import jsonify
import os

app = Flask(__name__)
api = Api(app)

app.config['MYSQL_HOST'] = "rozgaar.cdtf8jnpr7a9.ap-south-1.rds.amazonaws.com"
app.config['MYSQL_USER'] = "admin"
app.config['MYSQL_PASSWORD'] = "987654321"
app.config['MYSQL_DB'] = "newschema"

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

data = Flask(__name__)
data.config["IMAGE_UPLOADS"] = "/home/ubuntu/myflask/flask_python/static/profile/user"

data2 = Flask(__name__)
data2.config["IMAGE_UPLOADS"] = "/home/ubuntu/myflask/flask_python/static/profile/rec"

mysql = MySQL(app)

name_global_user = ''
name_global_rec = ''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#uplaod profile image of user
@app.route("/user/upload-image", methods=["GET", "POST"])
def upload_image():
    print("************** UPLOAD USER IMAGE **************")
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            user_id = request.form["user_id"]
            print("DATA:- ", "image: ", image, " user_id: ", user_id)
            image.save(os.path.join(data.config["IMAGE_UPLOADS"], image.filename))
            # return redirect(request.url)
            cur = mysql.connection.cursor()
            print(str(image.filename))
            cur.execute("UPDATE users SET image = %s WHERE phn_no = %s", (str(image.filename), user_id))
            mysql.connection.commit()
            cur.close()
            print("RETURN:- success")
            print("###########################################################\n")
            return "success"
    print("RETURN:- failed")
    print("###########################################################\n")
    return "none"

#uplaod profile image of recruiter
@app.route("/rec/upload-image", methods=["GET", "POST"])
def upload_image2():
    print("************** UPLOAD RECRUITER IMAGE **************")
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            user_id = request.form["user_id"]
            print("DATA:- ", "image: ", image, " user_id: ", user_id)
            image.save(os.path.join(data2.config["IMAGE_UPLOADS"], image.filename))
            # return redirect(request.url)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE recruiter SET image = %s WHERE phn_no = %s", (str(image.filename), user_id))
            mysql.connection.commit()
            cur.close()
            print("RETURN:- success")
            print("###########################################################\n")
            return "success"
    print("RETURN:- failed")
    print("###########################################################\n")
    return "none"

#get profile image of user
@app.route('/user/get_image', methods=["GET", "POST"])
def download_file():
    print("************** GET DATA: USER IMAGE **************")
    data = request.get_json()
    user_id = data['user_id']
    print("DATA:- ", "user_id: ", user_id)
    cur = mysql.connection.cursor()
    cur.execute("SELECT image FROM users WHERE phn_no = %s", [user_id])
    ls = cur.fetchall()
    for x in ls:
        for y in x:
            image = str(y)
    print("Return:- ", "image: ", image)
    print("###########################################################\n")
    return send_from_directory("/home/ubuntu/myflask/flask_python/static/profile/user", image, as_attachment=True)

#get profile image of user
@app.route('/rec/get_image', methods=["GET", "POST"])
def download_file2():
    print("************** GET DATA: RECRUITER IMAGE **************")
    data = request.get_json()
    user_id = data['user_id']
    print("DATA:- ", "user_id: ", user_id)
    cur = mysql.connection.cursor()
    cur.execute("SELECT image FROM recruiter WHERE phn_no = %s", [user_id])
    ls = cur.fetchall()
    for x in ls:
        for y in x:
            image = str(y)
    print("Return:- ", "image: ", image)
    print("###########################################################\n")
    return send_from_directory("/home/ubuntu/myflask/flask_python/static/profile/rec", image, as_attachment=True)

#get data for recruiter for rating user
@app.route('/user/rate/get_data', methods=['POST'])
def get_user_data():
    print("************** GET DATA: RECRUITER RATE USER **************")
    global jobid
    data = request.get_json()
    rec_id = data['rec_id']
    print("DATA:- ", "rec_id: ", rec_id)
    cur = mysql.connection.cursor()
    cur.execute('SELECT user_id, job_id, Id FROM applied WHERE (rec_id = %s and status = 1 and answer = 1 and user_star = 0)', [rec_id])
    user_id = cur.fetchall()
    user_id = list(user_id)
    user_id = reversed(user_id)
    ls = []
    ls_b = []
    ls_id = []
    dic_return_count = 0
    for x in user_id:
        id = str(x[0])
        jobid = str(x[1])
        idx = str(x[2])
        ls.append(id)
        ls_b.append(jobid)
        ls_id.append(idx)
    ls2 = []
    for y, z, z3 in zip(ls, ls_b, ls_id):
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM users WHERE phn_no = %s", [y])
        user_list = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
        job_data = cur3.fetchall()
        js = list(user_list)
        js2 = list(job_data)
        for x3, x4 in zip(js, js2):
            name = str(x3[0])
            user_phn = str(x3[1])
            type_job = str(x4[0])
            dic = {'name': name, 'phone': user_phn, 'job_type': type_job, 'apply_id': z3}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)

#set user rating, rated by recruiter
@app.route('/user/rate', methods=['POST'])
def user_rate():
    print("************** RECRUITER RATED USER **************")
    data = request.get_json()
    user_id = data['user_id']
    user_star = data['user_star']
    apply_id = data['apply_id']
    print("DATA:- ", "user_id: ", user_id, " user_star: ", user_star, " apply_id: ", apply_id)
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT * FROM users WHERE phn_no = %s", [user_id])
    cur3 = mysql.connection.cursor()
    cur3.execute("UPDATE applied SET user_star = %s WHERE Id = %s", [user_star, apply_id])
    mysql.connection.commit()
    rate = cur2.fetchall()
    for x in rate:
        r = x[2]

    try:
        r = int(r)
        if r == 0:
            rating = float(user_star)
        else:
            rating = (float(r) + float(user_star)) / 2
    except:
        rating = float(user_star)
    rating = int(rating)
    print("Rated: ", rating, " To: ", user_id)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE `users` SET `1`= %s WHERE `users`.`phn_no` = %s;", [rating, user_id])
    mysql.connection.commit()
    cur.close()
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#get star data of recruiter
@app.route('/rec/rate/get_data', methods=['POST'])
def get_rec_data():
    print("************** GET DATA: USER RATE RECRUITER **************")
    global jobid
    data = request.get_json()
    user_id = data['user_id']
    print("DATA:- ", "user_id: ", user_id)
    cur = mysql.connection.cursor()
    cur.execute('SELECT rec_id, job_id, Id FROM applied WHERE (user_id = %s and status = 1 and answer = 1 and rec_star = 0)', [user_id])
    user_id = cur.fetchall()
    user_id = list(user_id)
    user_id = reversed(user_id)
    ls = []
    ls_b = []
    ls_id = []
    dic_return_count = 0
    for x in user_id:
        id = str(x[0])
        jobid = str(x[1])
        idx = str(x[2])
        ls.append(id)
        ls_b.append(jobid)
        ls_id.append(idx)
    ls2 = []
    for y, z, z3 in zip(ls, ls_b, ls_id):
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM recruiter WHERE phn_no = %s", [y])
        user_list = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
        job_data = cur3.fetchall()
        js = list(user_list)
        js2 = list(job_data)
        for x3, x4 in zip(js, js2):
            name = str(x3[0])
            rec_phn = str(x3[1])
            type_job = str(x4[0])
            dic = {'name': name, 'phone': rec_phn, 'job_type': type_job, 'apply_id': z3}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)

#set recruiter rating, rated by user
@app.route('/recruiter/rate', methods=['POST'])
def recruiter_rate():
    print("************** USER RATED RECRUITER **************")
    data = request.get_json()
    user_id = data['rec_id']
    user_star = data['user_star']
    apply_id = data['apply_id']
    print("DATA:- ", "rec_id: ", user_id, " user_star: ", user_star, " apply_id: ", apply_id)
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT * FROM recruiter WHERE phn_no = %s", [user_id])
    cur3 = mysql.connection.cursor()
    cur3.execute("UPDATE applied SET rec_star = %s WHERE Id = %s", [user_star, apply_id])
    rate = cur2.fetchall()
    for x in rate:
        r = x[2]
    try:
        r = int(r)
        if r == 0:
            rating = float(user_star)
        else:
            rating = (float(r) + float(user_star)) / 2
    except:
        rating = float(user_star)
    print("Rated: ", rating, " To: ", user_id)
    rating = int(rating)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE `recruiter` SET `rate`= %s WHERE `recruiter`.`phn_no` = %s;", [rating, user_id])
    mysql.connection.commit()
    cur.close()
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#test mode
#fetch all users rows
@app.route('/users', methods=['GET','POST'])
def users():
    print("************** GET DATA: ALL USERS **************")
    cur = mysql.connection.cursor()
    users = cur.execute("SELECT * FROM users")
    if users > 0:
        userDetails = cur.fetchall()
        js = json.dumps(userDetails)
        print("RETURN:- ", js)
        print("###########################################################\n")
        return jsonify(js)

#for drop down, return all types of jobs, example: painter, driver, sweeper, etc
@app.route('/jobs_type', methods=['GET','POST'])
def jobs_type():
    print("************** GET DATA: JOB TYPES **************")
    cur = mysql.connection.cursor()
    cur.execute("SELECT job_type FROM jobs")
    job_Detail = list(cur.fetchall())
    res = []
    [res.append(x) for x in job_Detail if x not in res]
    print("RETURN:- ", res)
    print("###########################################################\n")
    return json.dumps(res)

#test mode
#fetch user by it's phone no.
@app.route('/user', methods=['GET','POST'])
def user():
    print("************** GET DATA: USER **************")
    data = request.get_json()
    phone = data['phone']
    print("DATA:- ", "phone", phone)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE phn_no = %s", [phone])
    userDetail = cur.fetchall()
    js = json.dumps(userDetail)
    print("RETURN:- ", js)
    print("###########################################################\n")
    return jsonify(js)

#for user dashboard, fetch all jobs according to job type
@app.route('/job/type', methods=['GET', 'POST'])
def get_joblist():
    print("************** GET DATA: JOBS FOR USER **************")
    global name_global_user
    data = request.get_json()
    type2 = data['type']
    status = str(data['status'])
    s_type = data['s_type']
    print("DATA:- ", "type: ", type2, " user_star: ", status, " s_type: ", s_type)
    cur = mysql.connection.cursor()
    if status == "false":
        s_type = ""
    if type2 == "all" and s_type == "none":
        cur.execute("SELECT * FROM jobs WHERE (del = 0 and status = %s)", (status))
    elif type2 == "all" and status == "true":
        cur.execute("SELECT * FROM jobs WHERE (del = 0 and status = %s and s_type = %s)", (status, s_type))
    elif type2 == "all":
        cur.execute("SELECT * FROM jobs WHERE (del = 0)")
    else:
        cur.execute("SELECT * FROM jobs WHERE (job_type = %s and del = 0 and status = %s, s_type = %s)", (type2, status, s_type))
    job_list = cur.fetchall()
    js = list(job_list)
    js = reversed(js)
    ls = []
    dic_return_count = 0
    for x in js:
        job_type = str(x[0])
        job_desc = str(x[1])
        rec_phn = str(x[2])
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT rate FROM recruiter WHERE phn_no = %s", [rec_phn])
        rate = cur2.fetchall()
        for i in rate:
            rate = i[0]
        alter_no = str(x[3])
        job_address = str(x[4])
        id = str(x[5])
        s_status = str(x[7])
        s_ret_type = str(x[8])
        if alter_no == "0":
            alter_no = ""
        dic = {'name': name_global_user, 'type': job_type, 'description': job_desc, 'phone': rec_phn, 'address': job_address, 'alternate': alter_no, 'id': id, 's_status': s_status, 's_ret_type': s_ret_type, 'rate': rate}
        dic = dict(dic)
        dic_return_count += 1
        print("Return:- ", dic_return_count, ": ", dic, "\n")
        ls.append(dic)
    print("###########################################################\n")
    return json.dumps(ls)

# for recruiter dashboard, fetch all job posted by recruiter while sorting with it's mobile no.
@app.route('/job/list', methods=['GET', 'POST'])
def get_job_rec():
    print("************** GET DATA: JOBS FOR RECRUITER **************")
    global name_global_rec
    data = request.get_json()
    phone = data['phone']
    print("DATA:- ", "phone: ", phone)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobs WHERE (rec_phn_no = %s and del = 0)", [phone])
    # cur.execute("SELECT * FROM `jobs` WHERE rec_phn_no = %s ORDER BY `jobs`.`Id` DESC", [phone])
    job_list = cur.fetchall()
    js = list(job_list)
    js = reversed(js)
    ls = []
    dic_return_count = 0
    for x in js:
        job_type = str(x[0])
        job_desc = str(x[1])
        rec_phn = str(x[2])
        alter_no = str(x[3])
        job_address = str(x[4])
        id = str(x[5])
        s_status = str(x[7])
        s_ret_type = str(x[8])
        if alter_no == "0":
            alter_no = ""
        dic = {'name': name_global_rec, 'type': job_type, 'description': job_desc, 'phone': rec_phn, 'address': job_address, 'alternate': alter_no, 'id': id, 'status': s_status, 's_type': s_ret_type}
        dic = dict(dic)
        dic_return_count += 1
        print("Return:- ", dic_return_count, ": ", dic, "\n")
        ls.append(dic)
    print("###########################################################\n")
    return json.dumps(ls)

# @app.route('/get/user/name', methods=['GET', 'POST'])
# def get_user_name():
#     global name_global_rec
#     print(name_global_rec)
#     data = request.get_json()
#     phone = data['phone']
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM jobs WHERE rec_phn_no = %s", [phone])
#     job_list = cur.fetchall()
#     js = list(job_list)
#     js = reversed(js)
#     ls = []
#     print("response format", js)
#     for x in js:
#         job_type = str(x[0])
#         job_desc = str(x[1])
#         rec_phn = str(x[2])
#         alter_no = str(x[3])
#         job_address = str(x[4])
#         id = str(x[5])
#         dic = {'name': name_global_rec, 'type': job_type, 'description': job_desc, 'phone': rec_phn, 'address': job_address, 'alternate': alter_no, 'id': id}
#         dic = dict(dic)
#         ls.append(dic)
#     print(ls)
#     return json.dumps(ls)

#when user apply into any job, or simply when press call button
@app.route('/user/apply', methods=['POST'])
def apply_oncall():
    print("************** CALL BUTTON PRESSED **************")
    data = request.get_json()
    user_id = data['user_id']
    job_id = data['job_id']
    rec_id = data['rec_id']
    print("DATA:- ", "user_id: ", user_id, " job_id: ", job_id, " rec_id: ", rec_id)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO applied (job_id, user_id, rec_id) VALUES (%s, %s, %s)", (job_id, user_id, rec_id))
    mysql.connection.commit()
    cur.close()
    print("RETURN:- success")
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#for rec notification page, gets all user that applied jobs, posted by him
@app.route('/user/apply/get', methods=['POST'])
def get_notfication():
    print("************** GET DATA: NOTIFICATION OF RECRUITER **************")
    global jobid
    data = request.get_json()
    rec_id = data['rec_id']
    print("DATA:- ", "rec_id: ", rec_id)
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, job_id, Id FROM applied WHERE (rec_id = %s and status = 0)", [rec_id])
    user_id = cur.fetchall()
    user_id = list(user_id)
    user_id = reversed(user_id)
    ls = []
    ls_b = []
    ls_id = []
    dic_return_count = 0
    for x in user_id:
        id = str(x[0])
        jobid = str(x[1])
        idx = str(x[2])
        ls.append(id)
        ls_b.append(jobid)
        ls_id.append(idx)
    ls2 = []
    for y, z, z3 in zip(ls, ls_b, ls_id):
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM users WHERE phn_no = %s", [y])
        user_list = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
        job_data = cur3.fetchall()
        js = list(user_list)
        js2 = list(job_data)
        for x3, x4 in zip(js, js2):
            name = str(x3[0])
            user_phn = str(x3[1])
            rate = str(x3[2])
            type_job = str(x4[0])
            dic = {'name': name, 'phone': user_phn, 'job_type': type_job, 'id': z3, 'rate': rate}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)


# func to add user data
@app.route('/add/user', methods=['POST'])
def add_user():
    print("************** ADD USER **************")
    global name_global_user
    data = request.get_json()
    name = data['name']
    name_global_user = data['name']
    phone = data['phone']
    status = str(data['status'])
    s_type = data['s_type']
    print("DATA:- ", "name: ", name, " phone: ", phone, " status: ", status, " s_type: ", s_type)
    if status == 'false':
        s_type = ""
    if s_type == "All":
        s_type = "none"
    if s_type == "Others":
        s_type = "none"
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT phn_no FROM users WHERE phn_no = %s", [phone])
    phn_chk = cur2.fetchall()
    if (len(phn_chk) > 0):
        print(phn_chk, phone)
        for x in phn_chk:
            y = int(x[0])
            if int(phone) == y:
                print("RETURN:- success with login")
                print("###########################################################\n")
                return jsonify({'status': 200, 'result': "success", 'role': "user", 'type': "login"})
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (name, phn_no, status, s_type) VALUES (%s,%s,%s,%s)", (name, phone, status, s_type))
                mysql.connection.commit()
                cur.close()
                print("RETURN:- success with sign up")
                print("###########################################################\n")
                return jsonify({'status': 200, 'result': "success", 'role': "user", 'type': "sign up"})
    else:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, phn_no, status, s_type) VALUES (%s,%s,%s,%s)", (name, phone, status, s_type))
        mysql.connection.commit()
        cur.close()
        print("RETURN:- success with sign up")
        print("###########################################################\n")
        return jsonify({'status': 200, 'result': "success", 'role': "user", 'type': "sign up"})


# func to add recruiter data
@app.route('/add/rec', methods=['POST'])
def add_rec():
    print("************** ADD RECRUITER **************")
    global name_global_rec
    data = request.get_json()
    name = data['name']
    name_global_rec = data['name']
    phone = data['phone']
    print("DATA:- ", "name: ", name, " phone: ", phone)
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT phn_no FROM recruiter WHERE phn_no = %s", [phone])
    phn_chk = cur2.fetchall()
    if(len(phn_chk) > 0):
        for x in phn_chk:
            y = int(x[0])
            if int(phone) == y:
                print("RETURN:- success with login")
                print("###########################################################\n")
                return jsonify({'status': 200, 'result': "success", 'role': "recruiter", 'type': "login"})
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO recruiter (name, phn_no) VALUES (%s,%s)", (name, phone))
                mysql.connection.commit()
                cur.close()
                print("RETURN:- success with sign up")
                print("###########################################################\n")
                return jsonify({'status': 200, 'result': "success", 'role': "recruiter", 'type': "sign up"})
    else:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO recruiter (name, phn_no) VALUES (%s,%s)", (name, phone))
        mysql.connection.commit()
        cur.close()
        print("RETURN:- success with sign up")
        print("###########################################################\n")
        return jsonify({'status': 200, 'result': "success", 'role': "recruiter", 'type': "sign up"})


# func to add job data
@app.route('/add/job', methods=['POST'])
def add_job():
    print("************** ADD JOB **************")
    data = request.get_json()
    phone = data['phone']
    address = data['address']
    job_type = data['type']
    job_dis = data['description']
    alt_no = data['alt_no']
    status = data['status']
    s_type = data['s_type']
    print("DATA:- ", "phone: ", phone, " address: ", address, " type: ", job_type, " description: ", job_dis, " alt_no: ", alt_no, " status: ", status, " s_type: ", s_type)
    if status == True:
        status2 = "true"
    if status == False:
        status2 = "false"
        s_type = ""
    if s_type == "All":
        s_type = "none"
    if s_type == "Others":
        s_type = "none"
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO jobs (job_type, job_desc, rec_phn_no, address, rec_alternate_no, status, s_type) VALUES (%s,%s,%s,%s,%s,%s,%s)", (job_type, job_dis, phone, address, alt_no, status2, s_type))
    mysql.connection.commit()
    cur.close()
    print("RETURN:- success")
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#rec end, to accept the user for the job
@app.route('/clicked/yes', methods=['POST'])
def yes():
    print("************** CLICKED YES **************")
    data = request.get_json()
    id = data['Id']
    print("DATA:- ", "Id: ", id)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE `applied` SET `status`='1',`answer`='1' WHERE `applied`.`Id` = %s;", [id])
    mysql.connection.commit()
    cur.close()
    print("RETURN:- success")
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#rec end, to reject the user for the job
@app.route('/clicked/no', methods=['POST'])
def no():
    print("************** CLICKED NO **************")
    data = request.get_json()
    id = data['Id']
    print("DATA:- ", "Id: ", id)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE `applied` SET `status`='1',`answer`='2' WHERE `applied`.`Id` = %s;", [id])
    mysql.connection.commit()
    cur.close()
    print("RETURN:- success")
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#for applied jobs in user end, where he get the update of (not seen, accepted, rejected)
@app.route('/applied/user/jobs', methods=['POST'])
def get_applied_job_for_user():
    print("************** GET DATA: APPLIED JOBS BY USER **************")
    data = request.get_json()
    user_id = data['user_id']
    print("DATA:- ", "user_id: ", user_id)
    cur = mysql.connection.cursor()
    cur.execute("SELECT job_id, status, answer FROM applied WHERE (user_id = %s)", [user_id])
    job_list = cur.fetchall()
    job_list = list(job_list)
    ls = []
    status_ls = []
    answer_ls = []
    dic_return_count = 0
    for x in job_list:
        id = str(x[0])
        status = str(x[1])
        answer = str(x[2])
        ls.append(id)
        status_ls.append(status)
        answer_ls.append(answer)
    ls2 = []
    for y, y2, y3 in zip(ls, status_ls, answer_ls):
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM jobs WHERE Id = %s", [y])
        job_data = cur2.fetchall()
        js = list(job_data)
        for x in js:
            job_type = str(x[0])
            job_desc = str(x[1])
            rec_phn = str(x[2])
            alter_no = str(x[3])
            job_address = str(x[4])
            id2 = str(x[5])
            if alter_no == "0":
                alter_no = ""
            dic = {'type': job_type, 'description': job_desc, 'phone': rec_phn, 'address': job_address,
                   'alternate': alter_no, 'id': id2, 'status': y2, 'answer': y3}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)

#rec hstory, rec end
@app.route('/rec/history', methods=['POST'])
def rec_history_by_yes():
    print("************** GET DATA: RECRUITER HISTORY **************")
    data = request.get_json()
    rec_id = data['rec_id']
    print("DATA:- ", "red_id: ", rec_id)
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, job_id, Id FROM applied WHERE (rec_id = %s and status = 1 and answer = 1)", [rec_id])
    user_id = cur.fetchall()
    user_id = list(user_id)
    ls = []
    ls_b = []
    ls_id = []
    dic_return_count = 0
    for x in user_id:
        id = str(x[0])
        jobid = str(x[1])
        idx = str(x[2])
        ls.append(id)
        ls_b.append(jobid)
        ls_id.append(idx)
    ls2 = []
    for y, z, z3 in zip(ls, ls_b, ls_id):
        print(y, z, z3)
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM users WHERE phn_no = %s", [y])
        user_list = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
        job_data = cur3.fetchall()
        cur4 = mysql.connection.cursor()
        cur4.execute("SELECT * FROM recruiter WHERE phn_no = %s", [rec_id])
        rec_list = cur4.fetchall()
        js = list(user_list)
        js2 = list(job_data)
        js3 = list(rec_list)
        for x3, x4, x5 in zip(js, js2, js3):
            name = str(x3[0])
            user_phn = str(x3[1])
            type_job = str(x4[0])
            rec_name = str(x5[0])
            rec_phn = str(x5[1])
            dic = {'name': name, 'phone': user_phn, 'job_type': type_job, 'id': z3, 'rec_name': rec_name, 'rec_phn': rec_phn}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)

#to del any job, i mean - set del value to 1
@app.route('/del/job', methods=['POST'])
def del_job():
    print("************** DELETE JOB BY RECRUITER **************")
    data = request.get_json()
    id = data['job_id']
    print("DATA:- ", "job_id: ", id)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE jobs SET del = 1 WHERE Id = %s", [id])
    mysql.connection.commit()
    cur.close()
    print("RETURN:- success")
    print("###########################################################\n")
    return jsonify({'result': "success", 'status': 200})

#user history, seen from both end
@app.route('/user/history', methods=['POST'])
def user_history_by_yes():
    print("************** GET DATA: USER HISTORY **************")
    data = request.get_json()
    user_id2 = data['user_id']
    print("DATA:- ", "user_id: ", user_id2)
    cur = mysql.connection.cursor()
    cur.execute("SELECT rec_id, job_id, Id FROM applied WHERE (user_id = %s and status = 1 and answer = 1)", [user_id2])
    user_id = cur.fetchall()
    user_id = list(user_id)
    ls = []
    ls_b = []
    ls_id = []
    dic_return_count = 0
    for x in user_id:
        id = str(x[0])
        jobid = str(x[1])
        idx = str(x[2])
        ls.append(id)
        ls_b.append(jobid)
        ls_id.append(idx)
    ls2 = []
    for y, z, z3 in zip(ls, ls_b, ls_id):
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM recruiter WHERE phn_no = %s", [y])
        rec_list = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
        job_data = cur3.fetchall()
        cur4 = mysql.connection.cursor()
        cur4.execute("SELECT * FROM users WHERE phn_no = %s", [user_id2])
        user_list = cur4.fetchall()
        js = list(rec_list)
        js2 = list(job_data)
        js3 = list(user_list)
        for x3, x4, x5 in zip(js, js2, js3):
            name = str(x3[0])
            rec_phn = str(x3[1])
            type_job = str(x4[0])
            user_name = str(x5[0])
            user_phn = str(x5[1])
            dic = {'name': name, 'phone': rec_phn, 'job_type': type_job, 'id': z3, 'user_name': user_name, 'user_phn': user_phn}
            dic = dict(dic)
            dic_return_count += 1
            print("Return:- ", dic_return_count, ": ", dic, "\n")
            ls2.append(dic)
    print("###########################################################\n")
    return json.dumps(ls2)
# @app.route('/user/history/get', methods=['POST'])
# def get_notfication():
#     global jobid
#     data = request.get_json()
#     rec_id = data['rec_id']
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT user_id, job_id, Id FROM applied WHERE (rec_id = %s and status = 0)", [rec_id])
#     user_id = cur.fetchall()
#     user_id = list(user_id)
#     ls = []
#     ls_b = []
#     ls_id = []
#     for x in user_id:
#         id = str(x[0])
#         jobid = str(x[1])
#         idx = str(x[2])
#         ls.append(id)
#         ls_b.append(jobid)
#         ls_id.append(idx)
#     print(ls)
#     print(ls_b)
#     ls2 = []
#     for y, z, z3 in zip(ls, ls_b, ls_id):
#         print(y, z, z3)
#         cur2 = mysql.connection.cursor()
#         cur2.execute("SELECT * FROM users WHERE phn_no = %s", [y])
#         user_list = cur2.fetchall()
#         cur3 = mysql.connection.cursor()
#         cur3.execute("SELECT job_type FROM jobs WHERE Id = %s", [z])
#         job_data = cur3.fetchall()
#         js = list(user_list)
#         js2 = list(job_data)
#         for x3, x4 in zip(js, js2):
#             name = str(x3[0])
#             user_phn = str(x3[1])
#             type_job = str(x4[0])
#             dic = {'name': name, 'phone': user_phn, 'job_type': type_job, 'id': z3}
#             dic = dict(dic)
#             ls2.append(dic)
#     print(ls2)
#     return json.dumps(ls2)

#### to detele data ### test mode == user ### sort data == phone
# @app.route('/delete/<int:phone2>', methods=['POST'])
# def delete(phone2):
#     phone = phone2
#     cur2 = mysql.connection.cursor()
#     cur2.execute("DELETE FROM users WHERE phn_no = %s", phone)
#     mysql.connection.commit()
#     cur2.close()
#     return "deleted"

#test mode
#to reset the whole database
##*** warning don't press it ***##
@app.route('/del/all', methods=['GET', 'POST'])
def del_all():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!WARNING DATABASE DELETED!!")
    cur = mysql.connection.cursor()
    cur.execute("TRUNCATE TABLE recruiter")
    cur.execute("TRUNCATE TABLE jobs")
    cur.execute("TRUNCATE TABLE users")
    cur.execute("TRUNCATE TABLE applied")
    mysql.connection.commit()
    cur.close()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    return jsonify({'result': "success", 'status': 200})

if __name__ == '__main__':
    app.run(debug=True)
