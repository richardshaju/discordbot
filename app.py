import discord
from discord.ext import commands
import pymysql.cursors


connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="discordbot",
    cursorclass=pymysql.cursors.DictCursor,
)

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Bot is Ready")
    await bot.tree.sync()


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1236740819084640349)
    await channel.send(f"Welcome to the server, {member.mention}!")
    await member.send(f"Welcome to the server, {member.name}!")
    member.just_joined = True


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if hasattr(message.author, "just_joined") and message.author.just_joined:
        del message.just_joined
        return

    await message.reply("Whatsup Bro")

    words = message.content.split()

    with connection.cursor() as cursor:
        for word in words:
            cursor.execute(
                "INSERT INTO user_words (discord_id, word) VALUES (%s, %s)",
                (message.author.id, word),
            )
    connection.commit()

    await bot.process_commands(message)


@bot.tree.command(name="select-role", description="get most used words")
async def select_role(interaction: discord.Interaction, role: discord.Role):
    if role.name == "Paul" or role.name == "@everyone":
        await interaction.response.send_message("Don't be over smart")
        return

    with connection.cursor() as cursor:
        cursor.execute("SELECT discord_id FROM user_role WHERE role = %s", (role.name))
        result = cursor.fetchall()

    if result:
        await interaction.response.send_message(f"{role.name} role is already occupied")
    else:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT discord_id FROM user_role WHERE discord_id = %s",
                (interaction.user.id,),
            )
            count = cursor.fetchall()
    if count:
        await interaction.response.send_message(
            "You are already in a role. One role at a time"
        )
    else:

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_role (discord_id, role) VALUES (%s, %s)",
                (interaction.user.id, role),
            )
            connection.commit()
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"{role.name} role is assigned to you")


@bot.tree.command(name="word_status", description="get most used words")
async def word_status(interaction):

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT word, COUNT(*) AS count FROM user_words GROUP BY word ORDER BY count DESC LIMIT 10"
        )
        result = cursor.fetchall()

    output = "\n".join(f'{row["word"]}: {row["count"]}' for row in result)
    await interaction.response.send_message(f"The 10 most used words are:\n{output}")


@bot.tree.command(name="user_status", description="get most used words")
async def user_status(ctx, user: discord.Member):

    # to check Bot
    if user.id == 1236563378064064562:
        await ctx.response.send_message("Don't play with me my boi")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT word, COUNT(*) AS count FROM user_words WHERE discord_id = %s GROUP BY word ORDER BY count DESC LIMIT 10",
            (user.id,),
        )
        result = cursor.fetchall()

    output = "\n".join(f'{row["word"]}: {row["count"]}' for row in result)
    await ctx.response.send_message(
        f"The 10 most used words by {user.display_name} are:\n{output}"
    )


bot.run('TOKEN')
