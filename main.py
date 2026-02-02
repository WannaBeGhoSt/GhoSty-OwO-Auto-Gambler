import discord
from discord.ext import commands
import asyncio
import json
import random
import re
import unicodedata
import sys
import os as brutality_ghosty

brutality_ghosty.system("pip install -r requirements.txt")
brutality_ghosty.system(
    "sleep 2 && clear >/dev/null 2>&1 &"
    if brutality_ghosty.name == "posix"
    else "timeout /t 2 >nul 2>&1 && cls"
)

print("Started GhoSty OwO Auto Gambler V2 - Async Development\nVer - 020226.2.0.0 - GhoSty")

GhoStyMainCommandDQ = {}

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        CONTROLLER_TOKEN = config.get('main_token')
        CONTROLLER_ID = int(config.get('main_id'))
except Exception as e:
    print("Error loading config.json. Ensure 'main_token' and 'main_id' exist.")
    sys.exit()

try:
    with open('tokens.txt', 'r') as f:
        WORKER_TOKENS = [line.strip() for line in f if line.strip()]
except Exception as e:
    print("Error loading tokens.txt.")
    sys.exit()

active_channels = []

class GhoStyOwOAutoGamblerMainO(commands.Bot):
    def __init__(self, token, worker_id, is_controller=False):
        super().__init__(command_prefix='.', self_bot=True, help_command=None)
        self.token_str = token
        self.worker_id = worker_id
        self.last_processed_msg_id = None
        self.is_controller = is_controller
        self.grind_running = False
        self.current_channel = None
        
        # ----------------------you can change this sequence as per your needs--------------------------
        self.bet_sequence = [1, 4, 20, 100, 500, 1500, 5015, 11946, 25020, 46507, 93555, 184200, 250000]
        # ----------------------------------------+-------------------------------------------------------
        self.seq_index = 0

    async def on_ready(self):
        role = "CONTROLLER" if self.is_controller else f"WORKER {self.worker_id}"
        print(f'Logged in as: {self.user} | Role: {role}')
    
        if not self.is_controller:
            self.loop.create_task(self.poll_GhoStyMainCommandDQ())

    async def check_warning(self, ctx):
        if not self.grind_running:
            return False

        try:
            messages = await ctx.channel.history(limit=10).flatten()

            for msg in messages:
                msg_content = str(msg.content)
                if not msg_content:
                    continue
                
                msg_content_clean = unicodedata.normalize("NFKC", msg_content)
                msg_content_clean = re.sub(r'[\u200B-\u200D\uFEFF]', '', msg_content_clean)
                msg_content_lower = msg_content_clean.lower()

                if "captcha" in msg_content_lower and "verify" in msg_content_lower:
                    warning_pattern = r'[\(\[\{]?\s*(\d+)\s*[\/ï¼]\s*5\s*[\)\]\}]?'
                    match = re.search(warning_pattern, msg_content_lower)

                    if match:
                        warning_count = int(match.group(1))
                        print(f"[{self.user.name}] ⚠️ CAPTCHA WARNING DETECTED: ({warning_count}/5)")

                        if warning_count >= 1:
                            self.grind_running = False
                            
                           
                            if ctx.channel.id in active_channels:
                                active_channels.remove(ctx.channel.id)

                            await ctx.send(
                                f"⚠ WARNING DETECTED! 🛑 Stopping Worker {self.worker_id} | **SOLVE YOUR CAPTCHA FIRST** | "
                                "Then Type `.start` again."
                            )
                            print(f"[{self.user.name}] ⚠ Stopped due to CAPTCHA (1/5)")
                            return True
            return False

        except Exception as e:
            print(f"Warning check error: {e}")
            return False

    async def grind_loop(self, ctx):
        self.seq_index = 0 
        channel = ctx.channel
        self.last_processed_msg_id = None

        print(f"[{self.user.name}] Starting grind in {channel.name}")
    

        initial_bet = self.bet_sequence[self.seq_index]
        await channel.send(f"owo cf {initial_bet}")
        print(f"[{self.user.name}] Sent initial bet: {initial_bet}")

        while self.grind_running:
            try:
                if await self.check_warning(ctx):
                    break

                await asyncio.sleep(4)
            
                owo_result = await self.find_owo_response(channel)
            
                if owo_result is None:
                    await asyncio.sleep(3)
                    continue

                if owo_result == "lost":
                    self.seq_index += 1
                    if self.seq_index >= len(self.bet_sequence):
                        self.seq_index = 0  
                    print(f"[{self.user.name}] Lost. Next bet will be: {self.bet_sequence[self.seq_index]}")
            
                elif owo_result == "won":
                    self.seq_index = 0
                    print(f"[{self.user.name}] Won! Resetting to: {self.bet_sequence[self.seq_index]}")

                sleep_time = random.uniform(13.7, 23.4) + random.choice([0.3, 0.7, 1.1, 1.4, 0.9, 1.6])
                await asyncio.sleep(sleep_time)

                if await self.check_warning(ctx):
                    break

                if self.grind_running:
                    next_bet = self.bet_sequence[self.seq_index]
                    await channel.send(f"owo cf {next_bet}")
                    print(f"[{self.user.name}] Sent bet: {next_bet}")

            except Exception as e:
                print(f"[{self.user.name}] Error in loop: {e}")
                await asyncio.sleep(5)

    async def find_owo_response(self, channel):
        try:
            messages = await channel.history(limit=20).flatten()
            
            for msg in messages:
                if self.last_processed_msg_id and msg.id == self.last_processed_msg_id:
                    break
                
                if msg.author.id != 408785106942164992:
                    continue
                
                content = msg.content.lower()
                
                if "you lost" in content:
                    self.last_processed_msg_id = msg.id
                    return "lost"
                elif "you won" in content:
                    self.last_processed_msg_id = msg.id
                    return "won"
            
            return None
            
        except Exception as e:
            print(f"Error polling history: {e}")
            return None
    
    async def execute_start(self, channel):
        if self.grind_running:
            await channel.send(f"⚠ [Worker {self.worker_id}] is already running!")
            return
    
        if channel.id in active_channels:
            await channel.send("⚠ This channel is already being used by another worker!")
            return
    
        self.grind_running = True
        self.current_channel = channel.id
        active_channels.append(channel.id)
        await channel.send(f"✅ [Worker {self.worker_id}] Started Grinding.")
        self.loop.create_task(self.grind_loop(await self.get_context(channel)))

    async def execute_stop(self, channel):
        self.grind_running = False
        if self.current_channel in active_channels:
            active_channels.remove(self.current_channel)
        self.current_channel = None
        await channel.send(f"🛑 [Worker {self.worker_id}] Stopped.")

    async def get_context(self, channel):
        class ctxghostyfake:
            pass
        ctx = ctxghostyfake()
        ctx.channel = channel
        ctx.send = channel.send
        return ctx

    async def poll_GhoStyMainCommandDQ(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self.worker_id in GhoStyMainCommandDQ:
                cmd = GhoStyMainCommandDQ.pop(self.worker_id)
                channel = self.get_channel(cmd['channel_id'])
                if channel:
                    if cmd['action'] == 'start':
                        await self.execute_start(channel)
                    elif cmd['action'] == 'stop':
                        await self.execute_stop(channel)
            await asyncio.sleep(1.5)

    async def on_message(self, message):
        if message.author.id != self.user.id:
            return

        content = message.content.lower().split()
        if not content:
            return
        cmd = content[0]
        if self.is_controller:
            if cmd == ".start" and len(content) > 1:
                target_id = int(content[1])
                GhoStyMainCommandDQ[target_id] = {
                    'action': 'start',
                    'channel_id': message.channel.id
                }
                await message.channel.send(f"📤 Start command queued for Worker {target_id}")
        
            elif cmd == ".stop" and len(content) > 1:
                target_id = int(content[1])
                GhoStyMainCommandDQ[target_id] = {
                    'action': 'stop',
                    'channel_id': message.channel.id
                }
                await message.channel.send(f"📤 Stop command queued for Worker {target_id}")
            return

        if cmd == ".start":
            await self.execute_start(message.channel)
    
        elif cmd == ".stop":
            await self.execute_stop(message.channel)


async def main():
    tasks = []

    if CONTROLLER_TOKEN:
        print("Initializing Controller...")
        controller_bot = GhoStyOwOAutoGamblerMainO(CONTROLLER_TOKEN, worker_id=0, is_controller=True)
        tasks.append(asyncio.create_task(ghosty_start_with_retry(controller_bot, CONTROLLER_TOKEN, "Controller")))

    if not WORKER_TOKENS:
        print("No tokens in tokens.txt")
    else:
        for i, token in enumerate(WORKER_TOKENS):
            w_id = i + 1
            print(f"Initializing Worker {w_id}...")
            bot = GhoStyOwOAutoGamblerMainO(token, worker_id=w_id, is_controller=False)
            tasks.append(asyncio.create_task(ghosty_start_with_retry(bot, token, f"Worker {w_id}")))
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def ghosty_start_with_retry(bot, token, bot_name, max_retries=3):
    for attempt in range(max_retries):
        try:
            await bot.start(token, bot=False)
            break
        except (ConnectionError, 
                TimeoutError,
                Exception) as e:
            error_name = type(e).__name__
            if "ServerDisconnectedError" in error_name or "ClientOSError" in error_name or "ConnectionError" in error_name:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"[{bot_name}] Connection error: {error_name}. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[{bot_name}] Failed to connect after {max_retries} attempts: {error_name}")
                    print(f"[{bot_name}] Error details: {str(e)}")
            else:
                print(f"[{bot_name}] Unexpected error: {error_name} - {str(e)}")
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:

        print("Shutting down...")
