import { 
  Client, 
  GatewayIntentBits, 
  PermissionsBitField, 
  SlashCommandBuilder, 
  REST, 
  Routes 
} from "discord.js";
import http from "http";

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages]
});

// Render uchun kichik server (o'chib qolmasligi uchun)
http.createServer((req, res) => {
  res.write("Bot is running!");
  res.end();
}).listen(process.env.PORT || 3000);

const commands = [
  // /del komandasi
  new SlashCommandBuilder()
    .setName('del')
    .setDescription('Xabarlarni ommaviy oʻchirish')
    .addIntegerOption(opt => opt.setName('soni').setDescription('1-100 gacha').setRequired(true)),

  // /delmute komandasi
  new SlashCommandBuilder()
    .setName('delmute')
    .setDescription('Xabarni oʻchirib, foydalanuvchini vaqtincha cheklash')
    .addUserOption(opt => opt.setName('user').setDescription('Foydalanuvchi').setRequired(true))
    .addStringOption(opt => opt.setName('limit').setDescription('Masalan: 10m, 1h, 1d').setRequired(true)),

  // /delwarn komandasi
  new SlashCommandBuilder()
    .setName('delwarn')
    .setDescription('Xabarni oʻchirib ogohlantirish berish')
    .addUserOption(opt => opt.setName('user').setDescription('Foydalanuvchi').setRequired(true))
    .addStringOption(opt => opt.setName('message').setDescription('Ogohlantirish matni').setRequired(true)),
].map(command => command.toJSON());

// Slash komandalarini Discord'ga yuborish
const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

client.once("ready", async () => {
  try {
    await rest.put(Routes.applicationCommands(client.user.id), { body: commands });
    console.log(`✅ Bot va slash komandalar tayyor: ${client.user.tag}`);
  } catch (error) {
    console.error(error);
  }
});

client.on("interactionCreate", async interaction => {
  if (!interaction.isChatInputCommand()) return;

  // Admin huquqini tekshirish
  if (!interaction.member.permissions.has(PermissionsBitField.Flags.Administrator)) {
    return interaction.reply({ content: "❌ Bu komandani faqat adminlar ishlata oladi!", ephemeral: true });
  }

  const { commandName, options } = interaction;

  // --- /del ---
  if (commandName === 'del') {
    const amount = options.getInteger('soni');
    await interaction.channel.bulkDelete(amount, true);
    await interaction.reply({ content: `🧹 ${amount} ta xabar oʻchirildi.`, ephemeral: true });
  }

  // --- /delmute ---
  if (commandName === 'delmute') {
    const user = options.getMember('user');
    const limit = options.getString('limit');
    
    const timeValue = parseInt(limit);
    const unit = limit.slice(-1);
    let duration = timeValue * 60 * 1000; // default m

    if (unit === 's') duration = timeValue * 1000;
    if (unit === 'h') duration = timeValue * 60 * 60 * 1000;
    if (unit === 'd') duration = timeValue * 24 * 60 * 60 * 1000;

    try {
      await user.timeout(duration);
      await interaction.reply({ content: `🔇 ${user} ${limit} muddatga mute qilindi.` });
    } catch (e) {
      await interaction.reply({ content: "❌ Xatolik: Botingizda 'Moderate Members' huquqi yo'q yoki foydalanuvchi yuqori rangda.", ephemeral: true });
    }
  }

  // --- /delwarn ---
  if (commandName === 'delwarn') {
    const user = options.getUser('user');
    const msg = options.getString('message');
    
    await interaction.reply({ content: `⚠️ ${user}, ${msg}` });
  }
});

client.login(process.env.DISCORD_TOKEN);
