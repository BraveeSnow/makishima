import { Client, Events, GatewayIntentBits } from "discord.js"
import dotenvx from "@dotenvx/dotenvx"

import logger from "@/logger"

dotenvx.config()

const client = new Client({
    intents: [GatewayIntentBits.GuildMessages],
})

client.once(Events.ClientReady, () => {
    logger.info(`Logged in as ${client.user?.displayName}`)
})

client.login(process.env["MAKISHIMA_TOKEN"])
