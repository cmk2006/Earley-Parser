import argparse
import sys
import string

from collections import defaultdict
from nltk.tree import Tree

#khai báo 1 quy luật theo 
class Rule(object):
	def __init__(self, lhs, rhs):
		self.lhs, self.rhs = lhs, rhs
  # đại diện cho luật từ trái sang phải, trong đó lhs k phải kết thúc và 
  # rhs gồm các giá trị đứng sau, có thể gồm giá trị kết thúc và không kết thúc
	def __contains__(self, sym):
		return sym in self.rhs
	def __eq__(self, other):
		if type(other) is Rule:
			return self.lhs == other.lhs and self.rhs == other.rhs
		return False
	def __getitem__(self, i):
		return self.rhs[i]
	def __len__(self):
		return len(self.rhs)
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return self.lhs + ' -> ' + ' '.join(self.rhs)

class Grammar(object):#đại diện cho 1 bộ ngữ pháp không ngữ cảnh
	def __init__(self):
		self.rules = defaultdict(list)
	#set quy luật trong danh sách từ trái qua phải
	def add(self, rule):
		self.rules[rule.lhs].append(rule)
	#thêm 1 quy luật vào bộ ngữ pháp
	@staticmethod
	def load_grammar(fpath):
		#load bộ ngữ pháp từ đường dẫn
		grammar = Grammar()
		with open(fpath) as f:
			for line in f:
				line = line.strip() #loại bỏ yếu tố dư
				if len(line) == 0:
					continue
				#thêm luật ngữ pháp vào bộ ngữ pháp
				entries = line.split('->')
				lhs = entries[0].strip()
				for rhs in entries[1].split('|'):
					grammar.add(Rule(lhs, rhs.strip().split()))
		return grammar

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		s = [str(r) for r in self.rules['S']]
		for nt, rule_list in self.rules.iteritems():
			if nt == 'S':
				continue
			s += [str(r) for r in rule_list]
		return '\n'.join(s)

	#trả ra quy luật của 1 từ k kết thúc
	def __getitem__(self, nt):
		return self.rules[nt]

	def is_terminal(self, sym):
		#kiểm tra từ có phải kết thúc
		return len(self.rules[sym]) == 0

	def is_tag(self, sym):
		#kiểm tra trạng thái của từ (đã xét, chưa xét, kết thúc/chưa kết thúc)
		if not self.is_terminal(sym):
			return all(self.is_terminal(s) for r in self.rules[sym] for s in
				r.rhs)
		return False


class EarleyState(object):
	#chỉ 1 trạng thái của thuật toán
	GAM = '<GAM>'

	def __init__(self, rule, dot=0, sent_pos=0, chart_pos=0, back_pointers=[]):
		self.rule = rule #khai báo 1 luật
		self.dot = dot #định vị vị trí của mốc xét
		self.sent_pos = sent_pos #định vị vị trí đang xét
		self.chart_pos = chart_pos
		#mốc chỉ tới các trạng thái trước (sử dụng nếu trạng thái được tạo ra bằng completer)
		self.back_pointers = back_pointers

	def __eq__(self, other):
		if type(other) is EarleyState:
			return self.rule == other.rule and self.dot == other.dot and \
				self.sent_pos == other.sent_pos
		return False

	def __len__(self):
		return len(self.rule)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		def str_helper(state):
			return ('(' + state.rule.lhs + ' -> ' +
			' '.join(state.rule.rhs[:state.dot] + ['*'] + 
				state.rule.rhs[state.dot:]) +
			(', [%d, %d])' % (state.sent_pos, state.chart_pos)))

		return (str_helper(self) +
			' (' + ', '.join(str_helper(s) for s in self.back_pointers) + ')')

	def next(self):
		#trả ra kí tự kế tiếp cần duyệt
		if self.dot < len(self):
			return self.rule[self.dot]

	def is_complete(self):
		#kiểm tra nếu trạng thái hiện tại đã hoàn thành chưa
		return len(self) == self.dot

	@staticmethod
	def init():
		#trả về trạng thái gốc của thuật toán
		return EarleyState(Rule(EarleyState.GAM, ['S']))


class ChartEntry(object):
	#đại diện cho 1 lần update trạng thái
	def __init__(self, states):
		self.states = states #danh sách các trạng thái

	def __iter__(self):
		return iter(self.states)

	def __len__(self):
		return len(self.states)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '\n'.join(str(s) for s in self.states)

	def add(self, state):
		#thêm trạng thái phân tích mới nếu nó chưa có sẵn
		if state not in self.states:
			self.states.append(state)


class Chart(object):
	#đại diện cho một bảng gồm các trạng tháii
  
	def __init__(self, entries):
		# List of chart entries.
		self.entries = entries

	def __getitem__(self, i):
		return self.entries[i]

	def __len__(self):
		return len(self.entries)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '\n\n'.join([("Chart[%d]:\n" % i) + str(entry) for i, entry in
			enumerate(self.entries)])

	@staticmethod
	def init(l):
		#khởi tạo chart với l lượt, bao gồm 1 lượt gốc ban đầu
		return Chart([(ChartEntry([]) if i > 0 else
				ChartEntry([EarleyState.init()])) for i in range(l)])


class EarleyParse(object):
	#các lệnh duyệt của 1 câu 
	def __init__(self, sentence, grammar):
		self.words = sentence.split()
		self.grammar = grammar
		#khai báo chart
		self.chart = Chart.init(len(self.words) + 1)

	def predictor(self, state, pos): #hàm dự đoán
		for rule in self.grammar[state.next()]:
			self.chart[pos].add(EarleyState(rule, dot=0,
				sent_pos=state.chart_pos, chart_pos=state.chart_pos))

	def scanner(self, state, pos):#hàm quét
		if state.chart_pos < len(self.words):
			word = self.words[state.chart_pos]

			if any((word in r) for r in self.grammar[state.next()]):
				self.chart[pos + 1].add(EarleyState(Rule(state.next(), [word]),
					dot=1, sent_pos=state.chart_pos,
					chart_pos=(state.chart_pos + 1)))

	def completer(self, state, pos):#hàm hoàn thành
		for prev_state in self.chart[state.sent_pos]:
			if prev_state.next() == state.rule.lhs:
				self.chart[pos].add(EarleyState(prev_state.rule,
					dot=(prev_state.dot + 1), sent_pos=prev_state.sent_pos,
					chart_pos=pos,
					back_pointers=(prev_state.back_pointers + [state])))

	def parse(self):
		#phân tách 1 câu 
		#kiểm tra thành phần kế tiếp trong câu đã có tag chưa
		def is_tag(state):
			return self.grammar.is_tag(state.next())

		for i in range(len(self.chart)):
			for state in self.chart[i]:
				if not state.is_complete():
					if is_tag(state):
						self.scanner(state, i)
					else:
						self.predictor(state, i)
				else:
					self.completer(state, i)

	def has_parse(self):
		#kiểm tra câu đã xét chưa
		for state in self.chart[-1]:
			if state.is_complete() and state.rule.lhs == 'S' and \
				state.sent_pos == 0 and state.chart_pos == len(self.words):
				return True

		return False

	def get(self):
		#trả về kết quả xét của câu
		def get_helper(state):
			if self.grammar.is_tag(state.rule.lhs):
				return Tree(state.rule.lhs, [state.rule.rhs[0]])

			return Tree(state.rule.lhs,
				[get_helper(s) for s in state.back_pointers])

		for state in self.chart[-1]:
			if state.is_complete() and state.rule.lhs == 'S' and \
				state.sent_pos == 0 and state.chart_pos == len(self.words):
				return get_helper(state)
		return None


def main():
	parser_description = ("Runs the Earley parser according to a given "
		"grammar.")
	
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('draw', nargs='?', default=False)
	parser.add_argument('grammar_file', help="Filepath to grammer file")

	args = parser.parse_args()

	grammar = Grammar.load_grammar(args.grammar_file)

	def run_parse(sentence):
		parse = EarleyParse(sentence, grammar)
		parse.parse()
		return parse.get()

	while True:
		try:
			sentence = input()
			#loại bỏ các thành phần dấu câu 
			stripped_sentence = sentence
			for p in string.punctuation:
				stripped_sentence = stripped_sentence.replace(p, '')
			parse = run_parse(stripped_sentence)
			#in câu gốc nếu không thể phân tách và vẽ nếu có thể.
			if parse is None:
				print (sentence + '\n')
			else:
				if args.draw:
					parse.draw()
				else:
					parse.pretty_print()
		except EOFError:
			sys.exit()

		if args.draw:
			sys.exit()
	
if __name__ == '__main__':
	main()
