import {
  Client,
  GatewayIntentBits,
  PermissionsBitField,
  Partials
} from "discord.js";

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers
  ],
  partials: [Partials.Channel]
});

// BOT READY
client.once("ready", () => {
  console.log(`✅ Bot ishga tushdi: ${client.user.tag}`);
});

// MESSAGE COMMANDS
client.on("messageCreate", async (message) => {
  if (message.author.bot) return;
  if (!message.guild) return;

  // Faqat admin/moderatorlar uchun
  if (
    !message.member.permissions.has(
      PermissionsBitField.Flags.Administrator
    )
  ) {
    return;
  }

  const args = message.content.split(" ");
  const command = args.shift().toLowerCase();

  // 🧹 !clear 10
  if (command === "!clear") {
    const amount = parseInt(args[0]);
    if (!amount || amount < 1 || amount > 100) {
      return message.reply("❌ 1 dan 100 gacha son yozing");
    }

    await message.channel.bulkDelete(amount, true);
    const msg = await message.channel.send(
      `🧹 ${amount} ta xabar o‘chirildi`
    );
    setTimeout(() => msg.delete(), 3000);
  }

  // 🔇 !mute @user 10
  if (command === "!mute") {
    const member = message.mentions.members.first();
    const minutes = parseInt(args[1]) || 10;

    if (!member)
      return message.reply("❌ Foydalanuvchini belgilang");

    await member.timeout(minutes * 60 * 1000);
    message.channel.send(
      `🔇 ${member.user.tag} ${minutes} daqiqaga mute qilindi`
    );
  }

  // 🔓 !unmute @user
  if (command === "!unmute") {
    const member = message.mentions.members.first();
    if (!member)
      return message.reply("❌ Foydalanuvchini belgilang");

    await member.timeout(null);
    message.channel.send(
      `🔓 ${member.user.tag} unmute qilindi`
    );
  }

  // 👢 !kick @user
  if (command === "!kick") {
    const member = message.mentions.members.first();
    if (!member)
      return message.reply("❌ Foydalanuvchini belgilang");

    await member.kick();
    message.channel.send(
      `👢 ${member.user.tag} serverdan chiqarildi`
    );
  }

  // 🚫 !ban @user
  if (command === "!ban") {
    const member = message.mentions.members.first();
    if (!member)
      return message.reply("❌ Foydalanuvchini belgilang");

    await member.ban({ reason: "Moderator tomonidan ban" });
    message.channel.send(
      `🚫 ${member.user.tag} ban qilindi`
    );
  }

  // ℹ️ !help
  if (command === "!help") {
    message.reply(`
🛡️ **Moderator buyruqlari**
!clear <1-100>
!mute @user <min>
!unmute @user
!kick @user
!ban @user
    `);
  }
});

// LOGIN
client.login(process.env.DISCORD_TOKEN);
