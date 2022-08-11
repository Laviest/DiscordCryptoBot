from asyncio import sleep
import requests, discord
from bs4 import BeautifulSoup
from discord.ext import commands

TOKEN = "MTAwNjE5NjgxNTk1MzE1NDA2OA.GlbZbL.mpLOp-olJZB3qUjbVX2REOeKBONQ_jL7WnCYYU"
client = commands.Bot(command_prefix=".")

BASE_URL = "https://www.coingecko.com"
requests_two = requests.get(BASE_URL).text
soup = BeautifulSoup(requests_two, "html.parser")

every_crypto = soup.find("div", class_="position-relative")
trOne = every_crypto.find_all("tr")


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('Mining for crypto'))

coin_name_list = []
coin_up_down_list = []
coin_price_list = []
old_prices_list = []

def get_cryptos():
    for index, crypto in enumerate(trOne):
        if index != 0:
            coin = crypto.find("span",
                               {"class": "lg:tw-flex font-bold tw-items-center tw-justify-between"}).text.strip()
            coin_shortcut = crypto.find("span", {
                "class": "d-lg-inline font-normal text-3xs tw-ml-0 md:tw-ml-2 md:tw-self-center tw-text-gray-500"}).text.strip()
            coin_price = crypto.find("td", {"class": "td-price price text-right pl-0"}).text.strip()
            last_hour = crypto.find("td", class_="td-change1h change1h stat-percent text-right col-market").text.strip()

            coin_name_list.append(f"{coin} ({coin_shortcut})")
            coin_price_list.append(coin_price)

            if '-' in last_hour:
                coin_up_down_list.append(
                    f"{coin_price}. In the last hour it has gone DOWN for {last_hour} :chart_with_downwards_trend:")
            else:
                coin_up_down_list.append(
                    f"{coin_price}.In the last hour it has gone UP for {last_hour} :chart_with_upwards_trend:")


last_24hours_coin = []
last_24hours_list = []


def last_24hours_change():
    for index, crypto in enumerate(trOne):
        if index != 0:
            coin = crypto.find("span",
                               {"class": "lg:tw-flex font-bold tw-items-center tw-justify-between"}).text.strip()
            last_24hours = crypto.find("td",
                                       class_="td-change24h change24h stat-percent text-right col-market").text.strip()
            coin_price = crypto.find("td", {"class": "td-price price text-right pl-0"}).text.strip()

            last_24hours_coin.append(coin)
            last_24hours_list.append(last_24hours)

            if "-" in last_24hours:
                last_24hours_percent = str(last_24hours).replace("-", "").replace("%", "")
                last_24hours_percent = int(float(last_24hours_percent))
                coin_price = str(coin_price).replace("$", "").replace(",", "")
                coin_price = int(float(coin_price))

                percent = ((last_24hours_percent / 100) * coin_price)
                old_prices_list.append(coin_price + percent)
            else:
                last_24hours_percent = str(last_24hours).replace("-", "").replace("%", "")
                last_24hours_percent = int(float(last_24hours_percent))
                coin_price = str(coin_price).replace("$", "").replace(",", "")
                coin_price = int(float(coin_price))

                percent = ((last_24hours_percent / 100) * coin_price)
                old_prices_list.append(coin_price - percent)


@client.command()
async def crypto(message, num: int):
    try:
        get_cryptos()
        embed = discord.Embed(
            colour=discord.Colour.green()
        )
        embed.set_footer(text="Made by PeroMaestro")
        embed.set_image(url="https://www.interactivebrokers.hu/images/web/cryptocurrency-hero.jpg")
        embed.set_author(name="Crypto prices",
                         icon_url="https://enterpriseviewpoint.com/wp-content/uploads/2022/02/bitcoin.jpg")
        number = 0

        while number < int(num):
            embed.add_field(name=coin_name_list[number], value=f"{coin_up_down_list[number]}", inline=False)
            number += 1
    except:
        embed = discord.Embed(
            title="Error",
            description="You haven't entered a number or the number you have entered is too high (maximum 55)",
            colour=discord.Colour.red()
        )

    await message.channel.send(embed=embed)


@client.command()
async def dailycrypto(message):
    get_cryptos()
    last_24hours_change()
    while True:
        try:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )
            embed.set_footer(text="Made by PeroMaestro")
            embed.set_image(url="https://www.interactivebrokers.hu/images/web/cryptocurrency-hero.jpg")
            embed.set_author(name="Crypto prices in the last 24 hours",
                             icon_url="https://enterpriseviewpoint.com/wp-content/uploads/2022/02/bitcoin.jpg")
            number = 0

            while number < 55:
                embed.add_field(name=last_24hours_coin[number] + " -> " + coin_price_list[number],
                                value=f"the price has changed for {last_24hours_list[number]},"
                                      f" old price was {old_prices_list[number]}", inline=False)
                number += 1
        except:
            embed = discord.Embed(
                title="Error",
                description="There is currently a problem with the bot.",
                colour=discord.Colour.red()
            )

        await sleep(86400)
        await message.channel.send(embed=embed)

client.run(TOKEN)
