			obj,created = SampleInfo.objects.get_or_create(
				sample_id = fields[8],
				sample_index = fields[21],
				species = fields[10].lower(),
				sample_type = fields[11].split('(')[0].strip(),
				preparation = fields[12].split('(')[0].strip(),
				description = fields[9],
				notes = fields[28]

			)