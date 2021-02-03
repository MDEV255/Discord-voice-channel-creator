# Discord-voice-channel-creator

[![Discord Bots](https://top.gg/api/widget/status/791601658651213824.svg)](https://top.gg/bot/791601658651213824)

A discord bot that will create a temporary voice channel

## Commands

commands| description
---|---
`vc create[?speaker] [?name]` | create a voice channel that everyone can hear
`vc private [?speaker] [?name]` | (coming soon) ~~create a  private voice channel that only speaker can hear~~
`vc change_log [?version]` | get recent change log
`vc permission` | get required permission
`vc help` | get command description

## Arguements

arg | Options
---|---
`?` | optional argument
`speaker` | - @user<br>- @role <br> Defalt speaker: @everyone
`name` | -channel name <br> Defalt: created by voice channel creator
`version` | -version number

## Example

command | result
---|---
vc create @gta casio heist | Channel name: gta casio heist <br> Speaker: you and user who have @gta role <br> Listener: everyone
vc create @Jason11ookJJ | Channel  name: Jason11ookJJ <br> Speaker: you and Jason11ookJJ <br> Listener: everyone
vc private @Jason11ookJJ |  Channel name: Jason11ookJJ <br> Speaker: you and Jason11ookJJ <br> Listener: you and Jason11ookJJ

---

## Hosting

As this bot is open source, you can host and edit this bot by yourself. I added some owner command to let you easier to edit and launch the bot.

Environment variable | data
---|---
OWNER | owner id
TOKEN | your bot token

command | use
--- | ---
`vc load [extension]` | load extension
`vc unload [extension]` | unload extension
`vc reload [extension]` | reload extension
`vc stats` | get bot stats
`vc resetdb` | reset database
