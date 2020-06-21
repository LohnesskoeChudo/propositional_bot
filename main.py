import logging
from aiogram import Bot, Dispatcher, executor, types
import mytoken
import logexps
import io

API_TOKEN = mytoken.token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_html(table):
	width = table.index('\n') + 1
	vw = 1.5 * round(100 / width,2)

	template = '''<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <title>Table</title>
  </head>
  <body style="font-size: 26px; white-space: nowrap;">
    <pre>%s</pre>
  </body>
</html>
'''
	html = template % table
	binary = io.BytesIO(html.encode('utf-8'))
	return types.input_file.InputFile(binary,filename="Result.html")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Hello! This bot will help you to get values of certain formula of proposition logic.')

@dp.message_handler(commands=['syntax'])
async def syntax(message: types.Message):
    answer = '''Operations:
    1. Disjunction:   A | B
    2. Conjuction:   A & B
    3. Implication:   A -> B
    4. Equivalence:   A <-> B
    5. Negation:   !A
Rules:
    1. Every compound expression must be wrapped in parenthesis.
    2. Whitespaces do not influence the result.
    3. Full expression may be not wrapped in parenthesis.
    4. To input multiple formulas separate them with ','.
Examples:
    A -> B
    (!A|!B)
    !A -> !(B & !(A))
    C->(A), A&B, A->(B <-> !C)'''
    await message.answer(answer)


@dp.message_handler()
async def handle_formulas(message: types.Message):
	formulas = message.text.split(sep=',')
	try:
		table = logexps.Table_maker(formulas)
	except logexps.IncorrectFormulaException:
		await message.answer('Wrong format. Type /syntax for help.')
		return
	except logexps.TooManyPropsException:
		await message.answer('Too many different propositionals in particular formula.')
		return
	except logexps.TooManyFormulasException:
		await message.answer('Too many formulas.')
		return
	except logexps.LengthException:
		await message.answer('One of formulas has too much symbols.')
		return

	str_table = table.get_table()
	html = get_html(str_table)
	await message.answer_document(html)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
