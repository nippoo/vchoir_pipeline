import os
import os.path as op
import configparser
import ffmpeg

source_dirs = "test_data/"
acceptable_input_formats = ['aa', 'aac', 'ac3', 'acm', 'adf', 'adp', 'dtk', 'ads', 'ss2', 'adx', 'aea', 'afc', 'aix', 'al', 'ape', 'apl', 'mac', 'aqt', 'ast', 'avi', 'avs', 'avr', 'bfstm', 'bcstm', 'bin', 'bit', 'bmv', 'brstm', 'cdg', 'cdxl', 'xl', '302', 'daud', 'str', 'dss', 'dts', 'dtshd', 'dv', 'dif', 'cdata', 'eac3', 'paf', 'fap', 'flm', 'flac', 'flv', 'fsb', 'g722', '722', 'tco', 'rco', 'g723_1', 'g729', 'genh', 'gsm', 'h261', 'h26l', 'h264', '264', 'avc', 'hevc', 'h265', '265', 'idf', 'cgi', 'sf', 'ircam', 'ivr', '669', 'amf', 'ams', 'dbm', 'digi', 'dmf', 'dsm', 'far', 'gdm', 'imf', 'it', 'j2b', 'm15', 'mdl', 'med', 'mmcmp', 'mms', 'mo3', 'mod', 'mptm', 'mt2', 'mtm', 'nst', 'okt', 'plm', 'ppm', 'psm', 'pt36', 'ptm', 's3m', 'sfx', 'sfx2', 'stk', 'stm', 'ult', 'umx', 'wow', 'xm', 'xpk', 'flv', 'lvf', 'm4v', 'mkv', 'mk3d', 'mka', 'mks', 'mjpg', 'mjpeg', 'mpo', 'j2k', 'mlp', 'mov', 'mp4', 'm4a', '3gp', '3g2', 'mj2', 'mp2', 'mp3', 'm2a', 'mpa', 'mpc', 'mjpg', 'txt', 'mpl2', 'sub', 'msf', 'mtaf', 'ul', 'musx', 'mvi', 'mxg', 'v', 'nist', 'sph', 'nut', 'ogg', 'oma', 'omg', 'aa3', 'pjs', 'pvf', 'yuv', 'cif', 'qcif', 'rgb', 'rt', 'rsd', 'rsd', 'rso', 'sw', 'sb', 'smi', 'sami', 'sbg', 'scc', 'sdr2', 'sds', 'sdx', 'shn', 'vb', 'son', 'sln', 'mjpg', 'stl', 'sub', 'sub', 'sup', 'svag', 'tak', 'thd', 'tta', 'ans', 'art', 'asc', 'diz', 'ice', 'nfo', 'txt', 'vt', 'uw', 'ub', 'v210', 'yuv10', 'vag', 'vc1', 'viv', 'idx', 'vpk', 'txt', 'vqf', 'vql', 'vqe', 'vtt', 'wsd', 'xmv', 'xvag', 'yop', 'y4m']

def rename_concat(input_base, output_dir):
	# Renames, concatenates files into one folder, prepending prefix
	for input_dir in dirs(input_base):
		for input_file in files(op.join(input_base, input_dir)):
			# Check if acceptable file extension:
			input_path = op.join(input_base, input_dir, input_file)
			if input_file.lower().endswith(tuple(acceptable_input_formats)):
				print("Moving {}".format(input_file))
				os.rename(input_path, op.join(output_dir, "{}_{}".format(input_dir, input_file)))

def split_audio(input_dir, output_dir, options):
	for input_file in files(input_dir):
		print("Extracting audio from {}".format(input_file))
		input_path = op.join(input_dir, input_file)
		input_basename, _ = op.splitext(input_file)
		output_path = op.join(output_dir, \
			"{}.{}".format(input_basename, options['filetype']))
		(
		    ffmpeg
		    .input(input_path)
		    .output(output_path, format=options['filetype'], \
		    	ar=int(options['sample_rate']), \
		    	ac=int(options['channels']), \
		    	sample_fmt=(options['bit_depth']))
		    .overwrite_output()
		    .run()
		)

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def dirs(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            yield file

if __name__ == "__main__":
	# Look at all projects, check if any of them need conversion.
	for project in dirs(source_dirs):
		basepath = op.join(source_dirs, project)
		print("Opening project: {}".format(project))
		try:
			parser = configparser.ConfigParser()
			parser.read(op.join(basepath, "config.ini"))
		except configparser.Error as err:
		    print('Could not parse: {}'.format(err))

		if parser['enable'].getboolean('rename_inputs'):
			rename_concat(op.join(basepath, parser['paths']['input_dirs']), \
				op.join(basepath, parser['paths']['rename_dir']))

		if parser['enable'].getboolean('split_audio'):
			split_audio(op.join(basepath, parser['paths']['rename_dir']), \
				op.join(basepath, parser['paths']['audio_output_dir']), \
				parser['audio'])
