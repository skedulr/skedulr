from flask import Flask, request, jsonify
from threading import Thread
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import requests
from urllib.parse import urljoin
from datetime import datetime


load_dotenv()

discord_token = os.environ.get('DISCORD_TOKEN')
backend = os.environ.get('BACKEND')

app = Flask(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_reply(self, arg):
        host = await bot.fetch_user(arg["host"])
        attendee = arg["attendee"]
        title = arg["title"]
        meet = arg["meet"]
        if meet:
            await host.send(f'{attendee} has confirmed attendance of the meeting {title}.')
        else:
            await host.send(f'{attendee} has declined attendance of the meeting {title}.')
        pass

    async def send_unclear(self, arg):
        user = await bot.fetch_user(arg["uid"])
        await user.send("I'm sorry, I couldn't catch that. Could you make that clearer?")
        pass


def run_discord_bot():

    @bot.event
    async def on_ready():
        await bot.add_cog(MyCog(bot))
        print('Bot is ready')

    @bot.event
    async def on_message(message):

        if message.author == bot.user:
            return

        # if DM
        if isinstance(message.channel, discord.DMChannel):
            response = requests.post(urljoin(backend, "/user/login"),
                                     json={"platform": "discord", "uid": message.author.id})
            if "loggedIn" not in response.json():
                # if not logged in
                await message.channel.send('Please enter your login credentials 🎯')
                await message.channel.send(response.json()["authorizationUrl"])
                # auth url sent as msg
            else:
                # user msg sent to backend
                await message.channel.send('Processing... 💯')

                try:
                    response = requests.post(
                        urljoin(backend, "/user/message"), json={"message": message.content, "platform": "discord", "uid": message.author.id})
                except Exception as error:
                    # clash of time or venue
                    await message.channel.send(f"An error occurred: {error}")
                    return

                parsed_message = response.json()
                start_time = parsed_message["start_date"]
                end_time = parsed_message["end_date"]
                place = parsed_message["location"]
                attendees = parsed_message["attendees"]
                title = parsed_message["summary"]

                # if start_time is None:
                #     await message.channel.send('Could you try that again, specifying the start date and time in the following format, please: (YYYY-MM-DDTHH:MM:SS) 😔')
                #     return
                # if end_time is None:
                #     await message.channel.send('Could you try that again, specifying the end date and time in the following format, please: (YYYY-MM-DDTHH:MM:SS) 😔')
                #     return
                # if place is None:
                #     await message.channel.send('Could you try that again, specifying the location of the meeting more clearly, please: 😔')
                #     return
                # if attendees is None:
                #     await message.channel.send('Could you try that again, specifying the list of attendees more clearly, please: 😔')
                #     return
                # if title is None:
                #     await message.channel.send('Could you try that again, specifying the title of the more clearly, please: 😔')
                #     return

                names = []
                for i in attendees:
                    names.append(i['name'])

                await message.channel.send(f"Verify the meeting details: \n ```Start Time 🕒: {start_time} \n End Time 🕒: {end_time} \n Location 🗺️: {place} \n Attendees 🧑‍🤝‍🧑: {names} \n Title: {title}```")

                if not (start_time is None or end_time is None or attendees is None or title is None or place is None):
                    view = Confirm()

                    await message.channel.send('Click the button to send the invite!', view=view)

                    # wait for button click
                    await view.wait()

                    parsed_message['platform'] = 'discord'
                    parsed_message['uid'] = message.author.id

                    if view.value:
                        response = requests.post(urljoin(backend, "/user/message-parsed"), json=parsed_message)
                        if response.status_code == 401:
                            await message.channel.send(f'There is a clash! : {response.json()["message"]} ☠️')
                        else:
                            await message.channel.send("Invite Sent! 🎯")

                    else:
                        await message.channel.send("Please try scheduling the meeting again then. 😔")
                        return
                else:
                    await message.channel.send("Please try scheduling the meeting again specifying the empty field more clearly. 😔")
                    return

    bot.run(discord_token)


@app.route('/reply', methods=['POST'])
def reply():
    my_cog = bot.get_cog('MyCog')
    data = request.json
    bot.loop.create_task(my_cog.send_reply(data))
    return jsonify({'message': 'DM sent!'})


if __name__ == '__main__':

    bot_thread = Thread(target=run_discord_bot)
    bot_thread.start()

    app.run()
