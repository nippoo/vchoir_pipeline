import os
import os.path as op
import configparser
from operator import itemgetter
import logging
from datetime import datetime
import time
import csv

import subprocess
import shlex

import newaaf

source_dirs = "Dropbox/15. VIDEO CONVERTER/"
# source_dirs = "actualtest_data/"
acceptable_input_formats = ['aa', 'aac', 'ac3', 'acm', 'adf', 'adp', 'dtk', 'ads', 'ss2', 'adx', 'aea', 'afc', 'aix', 'al', 'ape', 'apl', 'mac', 'aqt', 'ast', 'avi', 'avs', 'avr', 'bfstm', 'bcstm', 'bin', 'bit', 'bmv', 'brstm', 'cdg', 'cdxl', 'xl', '302', 'daud', 'str', 'dss', 'dts', 'dtshd', 'dv', 'dif', 'cdata', 'eac3', 'paf', 'fap', 'flm', 'flac', 'flv', 'fsb', 'g722', '722', 'tco', 'rco', 'g723_1', 'g729', 'genh', 'gsm', 'h261', 'h26l', 'h264', '264', 'avc', 'hevc', 'h265', '265', 'idf', 'cgi', 'sf', 'ircam', 'ivr', '669', 'amf', 'ams', 'dbm', 'digi', 'dmf', 'dsm', 'far', 'gdm', 'imf', 'it', 'j2b', 'm15', 'mdl', 'med', 'mmcmp', 'mms', 'mo3', 'mod', 'mptm', 'mt2', 'mtm', 'nst', 'okt', 'plm', 'ppm', 'psm', 'pt36', 'ptm', 's3m', 'sfx', 'sfx2', 'stk', 'stm', 'ult', 'umx', 'wow', 'xm', 'xpk', 'flv', 'lvf', 'm4v', 'mkv', 'mk3d', 'mka', 'mks', 'mjpg', 'mjpeg', 'mpo', 'j2k', 'mlp', 'mov', 'mp4', 'm4a', '3gp', '3g2', 'mj2', 'mp2', 'mp3', 'm2a', 'mpa', 'mpc', 'mjpg', 'txt', 'mpl2', 'sub', 'msf', 'mtaf', 'ul', 'musx', 'mvi', 'mxg', 'v', 'nist', 'sph', 'nut', 'ogg', 'oma', 'omg', 'aa3', 'pjs', 'pvf', 'yuv', 'cif', 'qcif', 'rgb', 'rt', 'rsd', 'rsd', 'rso', 'sw', 'sb', 'smi', 'sami', 'sbg', 'scc', 'sdr2', 'sds', 'sdx', 'shn', 'vb', 'son', 'sln', 'mjpg', 'stl', 'sub', 'sub', 'sup', 'svag', 'tak', 'thd', 'tta', 'ans', 'art', 'asc', 'diz', 'ice', 'nfo', 'txt', 'vt', 'uw', 'ub', 'v210', 'yuv10', 'vag', 'vc1', 'viv', 'idx', 'vpk', 'txt', 'vqf', 'vql', 'vqe', 'vtt', 'wsd', 'xmv', 'xvag', 'yop', 'y4m']

# def generate_blank(secs):
# 	(
# 		ffmpeg
# 		.input("anullsrc")
# 		.filter('lavfi', color='black', s="1920x1080", r="24000/1001")
# 		.output("test.mp4", ar='48000', ac='1', t='20')
# 	)

def rename_convert(input_base, output_dir, video_options, audio_options):
# Renames, concatenates files into one folder, prepending prefix

	old2new = [] # keep track of renamed files
	for input_dir in dirs(input_base):
		counter = 0 # reset counter to 0
		for input_file in files(op.join(input_base, input_dir)):
			# Check if acceptable file extension:
			input_path = op.join(input_base, input_dir, input_file)
			if input_file.lower().endswith(tuple(acceptable_input_formats)):
				output_file = f"{input_dir}_{counter:04d}.mp4"
				# input_basename, _ = op.splitext(input_file)
				# output_file = "{}_{}.mp4".format(input_dir, input_basename)
				output_path = op.join(output_dir, output_file)
				logging.info("Converting {} to {}".format(input_file, output_path))
				# os.rename(input_path, output_path)
				if os.path.exists(output_path):
					logging.error(f"Error, {output_path} already exists!")
				else:
					# current timestamp
					start = time.time()
					if convert_vid(input_path, output_path, video_options, audio_options):
						logging.warning(f"Failed to convert {input_file}!")
					else:
						old2new.append([input_file, output_file, (time.time()-start)])
						logging.info(f"Converted {input_file}!")
						counter += 1


	with open(op.join(input_base, 'old2new.csv'), mode='a') as csv_file:
		old2new_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
		old2new_writer.writerows([[a[0], a[1]] for a in old2new])

	now = datetime.now()

	with open('maxlog.csv', mode='a') as csv_file:
		old2new_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
		old2new_writer.writerow([f"Project: {input_base} at {now}"])
		old2new_writer.writerows([[a[0], a[2]] for a in old2new])

def convert_vid(input_path, output_path, video_options, audio_options):
# Converts an input file to an output with specified video, audio options

	w = video_options['width']
	h = video_options['height']

	fm_str = "ffmpeg -y -i {}".format(shlex.quote(input_path))

	fm_str += " -vcodec libx264 -crf 27 -preset veryfast -acodec copy"

	fm_str += " -r {}".format(video_options['framerate'])

	if video_options['scale_type'] == 'crop':
		fm_str += f' -vf "scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"'
	elif video_options['scale_type'] == 'letterbox':
		fm_str += f' -vf "scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"'
	elif video_options['scale_type'] == 'letterbox_noupscale':
		fm_str += f' -vf "scale=\'min({w},iw)\':min\'({h},ih)\':force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"'
	elif video_options['scale_type'] == 'constrain_preserve_original':
		fm_str += f' -vf "scale=\'2*floor(min({w},min(iw,round({h}*iw/ih)))/2)\':-2"'

	# fm_str += " -ar {}".format(audio_options['sample_rate'])
	# fm_str += " -ac {}".format(audio_options['channels'])
	fm_str += " {}".format(shlex.quote(output_path))

	logging.debug(fm_str)
	return subprocess.call(fm_str, shell=True)

def extract_audio(input_path, output_path, audio_options):
# Converts an input file to an output with specified video, audio options

	fm_str = "ffmpeg -y -i {}".format(shlex.quote(input_path))
	fm_str += " -ar {}".format(audio_options['sample_rate'])
	fm_str += " -ac {}".format(audio_options['channels'])
	fm_str += " -sample_fmt {}".format(audio_options['bit_depth'])
	fm_str += " {}".format(shlex.quote(output_path))

	subprocess.call(fm_str, shell=True)

def sync_aaf(input_dir, output_dir, aaf_file, options, audio_options):
	# first, try to open AAF and make list

	logging.info("Opening AAF file: {}".format(aaf_file))

	headers_lengths = (newaaf.list_headers_lengths(aaf_file))
	# find the longest header, subtract all other headers from that:
	trim_samples = [[a[0], (max(headers_lengths, key=itemgetter(1)))[1] - a[1]] for a in headers_lengths]

	for input_file in files(input_dir):
		print(input_file)
		input_path = op.join(input_dir, input_file)
		input_basename, _ = op.splitext(input_file)
		# check if input basename is in the list of header lengths:
		match = [item for item in trim_samples if item[0] == input_basename]
		if match:
			print("yay match! {}".format(match))
			output_path = op.join(output_dir, "{}.mp4".format(input_basename))

			fm_str = "ffmpeg -y -i {}".format(shlex.quote(input_path))
			fm_str += " -ss {}".format(match[0][1]/int(audio_options['sample_rate']))
			fm_str += " -vcodec copy"
			fm_str += " -ar {}".format(audio_options['sample_rate'])
			fm_str += " -ac {}".format(audio_options['channels'])
			fm_str += " {}".format(shlex.quote(output_path))

			logging.debug(fm_str)
			subprocess.call(fm_str, shell=True)
		else:
			logging.debug("Failed to match: {}".format(input_basename))

def split_audio(input_dir, output_dir, options):
	for input_file in files(input_dir):
		print("Extracting audio from {}".format(input_file))
		input_path = op.join(input_dir, input_file)
		input_basename, _ = op.splitext(input_file)
		output_path = op.join(output_dir, \
			"{}.{}".format(input_basename, options['filetype']))

		fm_str = "ffmpeg -y -i {}".format(shlex.quote(input_path))
		fm_str += " -ar {}".format(options['sample_rate'])
		fm_str += " -ac {}".format(options['channels'])
		fm_str += " -sample_fmt {}".format(options['bit_depth'])
		fm_str += " {}".format(shlex.quote(output_path))

		subprocess.call(fm_str, shell=True)

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def dirs(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            yield file

if __name__ == "__main__":

	# Initialize logging.
	logging.basicConfig(filename='vchoir_script.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

	# set up logging to console
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	# set a format which is simpler for console use
	formatter = logging.Formatter('%(asctime)s - %(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)

	# Look at all projects, check if any of them need anything doing.
	for project in dirs(source_dirs):
		basepath = op.join(source_dirs, project)
		logging.info("Opening project: {}".format(project))

		try:
			parser = configparser.ConfigParser()
			configfiles = parser.read(op.join(basepath, "config.ini"))
		except configparser.Error as err:
		    logging.warning('Could not parse: {}'.format(err))
		    continue

		if len(configfiles) == 0:
			logging.warning("Project: {} does not have a config.ini file, skipping".format(project))
			continue

		if parser['enable'].getboolean('convert_inputs'):
			rename_convert(op.join(basepath, parser['paths']['input_dirs']), \
				op.join(basepath, parser['paths']['convert_dir']), \
				parser['video'], \
				parser['audio'])
			parser['enable']['convert_inputs'] = "false"

		if parser['enable'].getboolean('split_audio'):
			split_audio(op.join(basepath, parser['paths']['convert_dir']), \
				op.join(basepath, parser['paths']['audio_output_dir']), \
				parser['audio'])
			parser['enable']['split_audio'] = "false"

		if parser['enable'].getboolean('sync_aaf'):
			sync_aaf(op.join(basepath, parser['paths']['convert_dir']), \
				op.join(basepath, parser['paths']['sync_output_dir']), \
				op.join(basepath, parser['paths']['aaf_file']), \
				parser['video'], \
				parser['audio'])
			parser['enable']['sync_aaf'] = "false"

		with open(op.join(basepath, "config.ini"), "w") as configfile:
			parser.write(configfile)
