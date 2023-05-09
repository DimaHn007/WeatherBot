from datetime import datetime

def print_weather(result, ide, place):
    answer = ''
    time = result[4]
    ref_time = datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M')
    print(f"Time\t\t: {ref_time}" )
    detail = result[3]
    temp = result[2]
    mint = result[5]
    maxt = result[6]
    feel = result[7]
    pres = result[8]
    hum = result[9]
    wind = result[10]
    #icon = result[11]

    answer += 'Дата: ' + ref_time + \
        "\n-------------------------------------------------------------\n"
    answer += 'В місті ' + place + " " + detail +"\n"
    answer += 'Температура 🌡: ' + str(temp) + "°C" + "\n"
    answer += 'Відчуття 🙎: ' + str(feel) + "\n"
    answer += 'Mінімальна ⬇: ' + str(mint) + "°C" + "\n" + 'Mаксимальна ⬆: ' + str(maxt) + "°C" + "\n"
    answer += 'Тиск 😬: ' + str(pres) + "\n"
    answer += 'Вологість 💧: ' + str(hum) + "%" + "\n"
    answer += 'Вітер 🌪: ' + str(wind) + "м/с" + \
        "\n-------------------------------------------------------------\n"

    if temp < 0:
        answer += 'На вулиці холодно, бери зимовий одяг!'
    elif temp < 18:
        answer += 'На вулиці холодно, одягайся тепліше!'
    elif temp > 18:
        answer += 'На вулиці тепло'
    return ide, answer