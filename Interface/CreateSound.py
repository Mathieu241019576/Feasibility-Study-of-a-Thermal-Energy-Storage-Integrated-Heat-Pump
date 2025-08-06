from Model_HTHP.__init__ import *


class CreateSound:
	def __init__(self, x=2):
		# With x, the octave multiplier
		# Notes frequency
		self.notes = {
			"Do":  261.63*x, "Do#":  277.18*x, "Ré♭":  277.18*x,
			"Ré":  293.66*x, "Ré#":  311.13*x, "Mi♭":  311.13*x,
			"Mi":  329.63*x, 
			"Fa":  349.23*x, "Fa#":  369.99*x, "Sol♭": 369.99*x,
			"Sol": 392.00*x, "Sol#": 415.30*x, "La♭":  415.30*x,
			"La":  440.00*x, "La#":  466.16*x, "Si♭":  466.16*x,
			"Si":  493.88*x
		}
	

	def sound1(self):
		
		# Melody
		chords = [
			(["Fa"],		0.2),
			(["Fa", "La"],	0.4),
			(["Sol"],		0.2),
			(["Sol", "Si"],	0.4),
			(["Do"],		0.2),
			(["Do", "Mi"],	0.4),
			(["Do", "Mi", "Sol"], 0.7)
		]

		sampling_rate = 44100 # Hz (Industrial standart)

		# y_note​(t)  = sin(2 * π * f_note * ​t)
		# y_chord​(t) = (1/n) * ∑ [ ​sin(2π * f_i * ​t) ]
		# song = y_note1 + y_chord1 + y_note2 + ...

		# Generate the melody
		song = np.hstack([
			sum(np.sin(2 * np.pi * self.notes[note] * np.linspace(0, duration, int(sampling_rate * duration), False))
				for note in chord) / len(chord)
			for chord, duration in chords
		])

		# Play the song
		sd.play(song, samplerate=sampling_rate)
		sd.wait()


	def sound2(self):
		# Melody and duration of each note
		melody = ["Sol", "Do"]
		durations = [0.5, 0.5]

		sampling_rate = 44100 # Hz (Industrial standart)

		# Generate the melody
		song = np.hstack([
			np.sin(2 * np.pi * self.notes[note] * np.linspace(0, dur, int(sampling_rate * dur), False))
			for note, dur in zip(melody, durations)
		])

		# Play the melody
		sd.play(song, samplerate=sampling_rate)
		sd.wait()