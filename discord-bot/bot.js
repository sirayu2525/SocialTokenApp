require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', async (message) => {
    if (message.content === '!register') {
        await message.reply('あなたのウォレットを作成中です…');
        // ここでウォレット作成の処理を呼び出す（次のステップで実装）
    }
});

client.login(process.env.DISCORD_BOT_TOKEN);
