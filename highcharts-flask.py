from flask import Flask, render_template, request, redirect, url_for,flash
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
import datetime
import os
import sys
import numpy as np
import datetime
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# On the home page - we select the file
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			todays_datetime_obj = datetime.datetime.now()
			fmt = '%Y_%m_%d_%H_%M_%S_%Z'
			datetime_string = datetime.datetime.strftime(todays_datetime_obj, fmt)
			filename = datetime_string + secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
	return render_template('index.html', uploadtobe = True)

# On uploading the file - the csv is read and populated in the dropdown in the stationform
# On selecting a station - onsubmit in the above form - we are redirected to a new page  with the station name
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
	if request.method == 'POST':
		station_name = request.form['stations']
		# print (station_name)
		# return redirect(url_for('uploaded_station', filename=filename, station_name=station_name))
		return redirect(url_for('charts', filename=filename, station_name=station_name))
	else:
		csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		new_df = pd.read_csv(csvpath, sep=',')
		all_stations = new_df['StationName'].unique()
		return render_template('index.html',filename=filename, stations = all_stations)

# On selecting the station name
@app.route('/uploads/<filename>/<station_name>', methods=['GET', 'POST'])
def uploaded_station(filename, station_name):
	if request.method == 'POST':
		device_id = request.form['devices']
		return redirect(url_for('uploaded_device', filename=filename, station_name=station_name, device_id=device_id))
	else:
		csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		new_df = pd.read_csv(csvpath, sep=',')
		all_devices = new_df[new_df['StationName']==station_name]['DeviceId'].unique()
		csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		new_df = pd.read_csv(csvpath, sep=',')
		all_stations = new_df['StationName'].unique()
		return render_template('index.html', filename=filename, stations=all_stations, devices = all_devices, station_name=station_name)

@app.route('/uploads/<filename>/<station_name>/<device_id>', methods=['GET', 'POST'])
def uploaded_device(filename, station_name, device_id):
	if request.method == 'POST':
		plato = request.form['plato']
		return redirect(url_for('uploaded_plato', filename=filename, station_name=station_name, device_id=device_id, plato=plato))
	else:
		csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		new_df = pd.read_csv(csvpath, sep=',')
		all_devices = new_df[new_df['StationName']==station_name]['DeviceId'].unique()
		csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		new_df = pd.read_csv(csvpath, sep=',')
		all_stations = new_df['StationName'].unique()
		# print(all_stations)
		# print (all_devices)
		return render_template('index.html', filename=filename, stations=all_stations, devices = all_devices, station_name=station_name, device_name=device_id)

@app.route('/uploads/<filename>/<station_name>/<device_id>/<plato>')
def uploaded_plato(filename, station_name, device_id, plato):
	return redirect(url_for('charts', filename=filename, station_name = station_name, device_id = device_id, plato=plato))

# @app.route('/charts/<filename>/<station_name>/<device_id>/<plato>')
@app.route('/charts/<filename>/<station_name>')
def charts(filename, station_name, chartID = 'chart_ID', chart_type = 'column', chart_height = 350):
	station_name = station_name
	device_id = 'All'
	plato = 'Cygnus'
	chart = []
	series = []
	title = []
	xAxis = []
	yAxis = []
	chartID = []

	
	# get the csv file
	csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	new_df = pd.read_csv(csvpath, sep=',')
	rats = new_df['Description'].unique()
	rats = dict(zip(rats, range(1, len(rats))))
	allrats = {'OOS': 1.0, 'NETWORK_TYPE_UNKNOWN': 2.0, 'IDEN': 3.0, '1xRTT': 4.0, 'CDMA': 5.0, 'EVDO_0': 6.0,
			   'EVDO_A': 7.0, 'EVDO_B+': 8.0, 'EHRPD': 9.0, 'GPRS': 10.0, 'EDGE': 11.0, 'UMTS': 12.0, 'TDSCDMA': 13.0,
			   'HSDPA': 14.0, 'HSUPA': 15.0, 'HSPA': 16.0, 'HSPA+': 17.0, 'IWLAN': 18.0, 'LTE': 19.0, 'LTE_CA': 20.0}
	
	
	temp = sorted(allrats.items(), key=lambda x: x[1])
	finalrats = {}
	
	x = 1
	reverserats = {}
	for i in temp:
		finalrats[i[0]] = x
		reverserats[x] = i[0]
		x += 1

	# get the uniqe csv ids.
	finalratslist = []
	device_ids = new_df[new_df['StationName'] == station_name]['DeviceId'].unique()
	new_descriptions_array_array = []
	if device_id == 'All':
		for i in range(len(device_ids)):
			new_df2 = new_df[new_df['DeviceId'] == device_ids[i]]
			#new_df2 = new_df[new_df['DeviceId'] == device_id]
			descriptions = new_df2['Description']
			new_descriptions = descriptions.map(allrats)
			new_descriptions_array_array.append(sorted(new_descriptions.unique().tolist() + [0]))
			times = new_df2['ResultTime']
			df = pd.DataFrame()
			df['Data'] = new_descriptions
			df.index = times
			station = new_df2['StationName'].unique()
			times_as_a_list = list(times)
			print('times',times_as_a_list)
			new_descriptions_as_a_list = list(new_descriptions)
			descriptions_as_a_list = list(descriptions)
			print ('tick positions - array - for desc_array', new_descriptions_array_array)
			print('tick  positions - list - for series', new_descriptions_as_a_list)
			chartID.append('chart_ID' + str(i))
			chart.append({"renderTo": chartID[i], "type": chart_type, "height": chart_height,})
			series.append([{"name": 'Cygnus Log', "data": new_descriptions_as_a_list}])
			title.append({"text": 'Cygnus Data for ' + str(device_ids[i])})
			xAxis.append({"categories": times_as_a_list})
			yAxis.append({"title": {"text": 'RAT Info'}})
	
	else:
		new_df2 = new_df[new_df['DeviceId'] == device_id]
		descriptions = new_df2['Description']
		new_descriptions = descriptions.map(allrats)
		new_descriptions_array_array.append(sorted(new_descriptions.unique().tolist() + [0]))
		times = new_df2['ResultTime']
		df = pd.DataFrame()
		df['Data'] = new_descriptions
		df.index = times
		station = new_df2['StationName'].unique()
		times_as_a_list = list(times)
		new_descriptions_as_a_list = list(new_descriptions)
		descriptions_as_a_list = list(descriptions)
		chartID.append('chart_ID' + str(1))
		chart.append({"renderTo": chartID[0], "type": chart_type, "height": chart_height})
		series.append([{"name": 'Cygnus Log', "data": new_descriptions_as_a_list}])
		title.append({"text": 'Cygnus Data for ' + str(device_id)})
		xAxis.append({"categories": times_as_a_list})
		yAxis.append({"title": {"text": 'RAT Info'}})
	
	csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	new_df = pd.read_csv(csvpath, sep=',')
	all_devices = new_df[new_df['StationName'] == station_name]['DeviceId'].unique()
	csvpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	new_df = pd.read_csv(csvpath, sep=',')
	all_stations = new_df['StationName'].unique()
	return render_template('index.html', desc_array=new_descriptions_array_array, filename=filename, stations=all_stations, devices=all_devices,
	 chartID=chartID, chart=chart, series=series, plato_name=plato, title=title, xAxis=xAxis, yAxis=yAxis, device_name=device_id, station_name=station_name)

if __name__ == "__main__":
	app.run(debug = True, host='127.0.0.1', port=4000, passthrough_errors=True, threaded = True)

