from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\All Semesters & Internships\Semester 6\CN\CN_ASSIGNMENT_F\CN_ASSIGNMENT_F\CN_ASSIGNMENT\instance\reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time_start = db.Column(db.String(10), nullable=False)
    time_finished = db.Column(db.String(10), nullable=False)

@app.route('/')
def index():
    return render_template('lab.html')

@app.route('/reserve', methods=['POST'])
def make_reservation():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time_start = request.form['time_start']
        time_finished = request.form['time_finished']
        
        reservation_time_start = datetime.strptime(time_start, '%H:%M')
        reservation_time_finished = datetime.strptime(time_finished, '%H:%M')
        existing_reservations = Reservation.query.filter_by(date=date).all()
        
        for reservation in existing_reservations:
            existing_time_start = datetime.strptime(reservation.time_start, '%H:%M')
            existing_time_finished = datetime.strptime(reservation.time_finished, '%H:%M')
            if (existing_time_start <= reservation_time_start < existing_time_finished) or (existing_time_start < reservation_time_finished <= existing_time_finished):
                return jsonify({'success': False, 'message': 'Cannot make reservation because it overlaps with an existing reservation'})
        
        with app.app_context():
            new_reservation = Reservation(name=name, date=date, time_start=time_start, time_finished=time_finished)
            db.session.add(new_reservation)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Reservation made successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid request'})

@app.route('/delete_reservation/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    try:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reservation deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/all_reservations')
def all_reservations():
    with app.app_context():
        reservations = Reservation.query.all()
    return render_template('reserve.html', reservations=reservations)

@app.route('/reset_reservations', methods=['POST'])  # New route for resetting reservations
def reset_reservations():
    try:
        db.session.query(Reservation).delete()  # Clearing all reservations
        db.session.commit()
        return jsonify({'success': True, 'message': 'All reservations reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/update_reservation', methods=['POST'])
def update_reservation():
    return redirect(url_for('all_reservations'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host="0.0.0.0")
