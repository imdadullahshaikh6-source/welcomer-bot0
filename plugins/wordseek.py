import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Active game state per group
GAMES = {}

# Comprehensive Word Dictionaries (Expanded Lists)
WORDS_4 = [
    "SPIN", "GRID", "FINE", "SHIN", "LOVE", "FIRE", "WIND", "RAIN", "SNOW", "STAR",
    "MOON", "GAME", "PLAY", "TIME", "LIFE", "DARK", "WARM", "COLD", "GOLD", "BLUE",
    "PINK", "ROSE", "LILY", "BIRD", "FISH", "LION", "BEAR", "WOLF", "FROG", "DUCK",
    "BOOK", "PAGE", "WORD", "SONG", "BEAT", "ROCK", "TREE", "LEAF", "WOOD", "DOOR",
    "WALL", "ROOM", "HOME", "CITY", "TOWN", "ROAD", "PATH", "HERO", "KING", "ZOYA",
    "CODE", "CHAT", "FAST", "SLOW", "COOL", "NICE", "GOOD", "LUCK", "MIND", "SOUL",
    "HOPE", "WISH", "TRUE", "FREE", "WAVE", "SAND", "SHIP", "BOAT", "PEAK", "HILL",
    "BABY", "BACK", "BAKE", "BALL", "BAND", "BANK", "BARK", "BARN", "BATH", "BEAM",
    "BELL", "BEST", "BIKE", "BILL", "BIRD", "BLOW", "BONE", "BORN", "BOWL", "BURN",
    "CAKE", "CALL", "CALM", "CAMP", "CARD", "CARE", "CASE", "CASH", "CAST", "CAVE",
    "CLAN", "CLAY", "CLIP", "CLUB", "COAL", "COAT", "COIN", "COOK", "COPY", "CORN",
    "CREW", "CROP", "CROW", "CURE", "DARE", "DATE", "DAWN", "DEAL", "DEAR", "DEEP",
    "DEER", "DESK", "DICE", "DIRT", "DISC", "DISH", "DOLL", "DOME", "DOSE", "DOWN",
    "DRAW", "DROP", "DRUM", "DUST", "DUTY", "EACH", "EARN", "EAST", "EASY", "EDGE",
    "EVEN", "EVER", "FACE", "FACT", "FAIR", "FALL", "FARM", "FAST", "FATE", "FEAR",
    "FEED", "FEEL", "FEET", "FILL", "FILM", "FIND", "FIRE", "FIRM", "FLAG", "FLAT",
    "FLOW", "FOOD", "FOOL", "FOOT", "FORK", "FORM", "FORT", "FOUR", "FREE", "FROG",
    "FUEL", "FULL", "GAIN", "GATE", "GEAR", "GIFT", "GIRL", "GIVE", "GLOW", "GOAL",
    "GOAT", "GOLD", "GRIP", "GROW", "HAIR", "HALF", "HALL", "HAND", "HANG", "HARD",
    "HARM", "HATE", "HEAD", "HEAL", "HEAR", "HEAT", "HELP", "HERB", "HIDE", "HIGH",
    "HOLD", "HOLE", "HOLY", "HOOK", "HOPE", "HORN", "HOST", "HOUR", "HUNT", "HURT",
    "ICON", "IDEA", "IRON", "ITEM", "JOIN", "JOKE", "JUMP", "JUST", "KEEP", "KICK",
    "KILL", "KIND", "KISS", "KITE", "KNEE", "KNOT", "KNOW", "LAKE", "LAMP", "LAND",
    "LANE", "LAST", "LATE", "LEAD", "LEAF", "LEAN", "LEFT", "LEND", "LINE", "LINK",
    "LION", "LIST", "LIVE", "LOAD", "LOCK", "LONG", "LOOK", "LORD", "LOSE", "LOSS",
    "LOUD", "LOVE", "LUCK", "LUNG", "MAIL", "MAIN", "MAKE", "MALE", "MALL", "MANY",
    "MARK", "MASK", "MASS", "MATE", "MEAL", "MEAT", "MEET", "MELT", "MILE", "MILK",
    "MILL", "MIND", "MINE", "MOON", "MOST", "MOVE", "MUCH", "NAME", "NAVY", "NEAR",
    "NEAT", "NECK", "NEED", "NEST", "NEWS", "NEXT", "NICE", "NIGHT", "NOON", "NOSE",
    "NOTE", "ONCE", "ONLY", "OPEN", "OVER", "PACE", "PACK", "PAGE", "PAIN", "PAIR",
    "PALM", "PARK", "PART", "PASS", "PAST", "PATH", "PEAK", "PEAR", "PICK", "PILE",
    "PINE", "PIPE", "PLAN", "PLAY", "PLOT", "PLUG", "POEM", "POET", "POLE", "POOL",
    "POOR", "PORT", "POST", "PULL", "PURE", "PUSH", "RACE", "RAIL", "RAIN", "RANK",
    "RARE", "RATE", "READ", "REAL", "REAR", "RELY", "RENT", "REST", "RICE", "RICH",
    "RIDE", "RING", "RISE", "RISK", "ROAD", "ROCK", "ROOF", "ROOT", "ROSE", "RULE",
    "RUSH", "SAFE", "SAIL", "SALT", "SAME", "SAND", "SAVE", "SEAT", "SEED", "SEEK",
    "SEEM", "SELF", "SELL", "SEND", "SHIP", "SHOE", "SHOP", "SHOT", "SHOW", "SHUT",
    "SICK", "SIDE", "SIGN", "SILK", "SING", "SINK", "SITE", "SIZE", "SKIN", "SLIP",
    "SLOW", "SNOW", "SOAP", "SOFT", "SOIL", "SOME", "SONG", "SOON", "SOUL", "SOUP",
    "SPOT", "STAR", "STAY", "STEP", "STOP", "SUIT", "SURE", "SWIM", "TALE", "TALK",
    "TALL", "TANK", "TAPE", "TASK", "TEAM", "TEAR", "TELL", "TENT", "TERM", "TEST",
    "TEXT", "THAT", "THEM", "THEN", "THEY", "THIN", "THIS", "TIDE", "TIE", "TIME",
    "TINY", "TIRE", "TOLL", "TONE", "TOOK", "TOOL", "TOUR", "TOWN", "TRAP", "TREE",
    "TRIP", "TRUE", "TUBE", "TUNE", "TURN", "TWIN", "TYPE", "UNIT", "UPON", "VAST",
    "VIEW", "VOTE", "WAGE", "WAIT", "WAKE", "WALK", "WALL", "WANT", "WARM", "WARN",
    "WASH", "WAVE", "WEAK", "WEAR", "WEEK", "WELL", "WEST", "WHAT", "WHEEL", "WHEN",
    "WIDE", "WIFE", "WILD", "WILL", "WIND", "WING", "WINK", "WIRE", "WISE", "WISH",
    "WITH", "WOLF", "WOOD", "WOOL", "WORD", "WORK", "WORM", "WRAP", "YARD", "YEAR",
    "ZERO", "ZONE"
]

WORDS_5 = [
    "HEART", "LIGHT", "NIGHT", "DREAM", "SMILE", "LAUGH", "WATER", "EARTH", "MUSIC",
    "DANCE", "SWEET", "HONEY", "MAGIC", "POWER", "TIGER", "PANDA", "APPLE", "MANGO",
    "OCEAN", "RIVER", "CLOUD", "STORM", "PEACE", "ANGEL", "QUEEN", "ROYAL", "BRAVE",
    "SMART", "SHINE", "SPARK", "VIBES", "STORY", "GHOST", "BLAZE", "FAITH", "GRACE",
    "HAPPY", "LUCKY", "SOLAR", "SPACE", "WORLD", "TRACK", "PLANT", "BLOOM", "CANDY",
    "ABOUT", "ABOVE", "ACTOR", "ADULT", "AFTER", "AGAIN", "AGENT", "AGREE", "AHEAD",
    "ALARM", "ALBUM", "ALERT", "ALIKE", "ALIVE", "ALLOW", "ALONE", "ALONG", "ALTER",
    "AMONG", "ANGER", "ANKLE", "APART", "APPLE", "APPLY", "ARENA", "ARGUE", "ARISE",
    "ARMED", "ARMOR", "ARROW", "ASIDE", "ASSET", "AVOID", "AWAIT", "AWAKE", "AWARD",
    "AWARE", "BADGE", "BASIC", "BASIS", "BEACH", "BEAST", "BEGIN", "BEING", "BELOW",
    "BENCH", "BERRY", "BIRTH", "BLACK", "BLADE", "BLAME", "BLANK", "BLAST", "BLEND",
    "BLESS", "BLIND", "BLOCK", "BLOOD", "BOARD", "BOAST", "BONUS", "BOOST", "BOUND",
    "BRAIN", "BRAND", "BREAD", "BREAK", "BREED", "BRIEF", "BRING", "BROAD", "BROWN",
    "BUILD", "BUNCH", "BUYER", "CABIN", "CABLE", "CAMEL", "CANAL", "CANDY", "CRAFT",
    "CRANE", "CRASH", "CRAWL", "CRAZY", "CREAM", "CRIME", "CROSS", "CROWD", "CROWN",
    "CRUSH", "DAILY", "DANCE", "DELAY", "DELTA", "DENSE", "DEVIL", "DIARY", "DRAFT",
    "DRAMA", "DREAM", "DRESS", "DRIFT", "DRINK", "DRIVE", "EAGER", "EARLY", "EARTH",
    "ELITE", "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY", "EQUAL", "ERROR", "EVENT",
    "EXACT", "EXIST", "EXTRA", "FAITH", "FALSE", "FANCY", "FAULT", "FAVOR", "FEAST",
    "FIBER", "FIELD", "FIFTH", "FIFTY", "FIGHT", "FINAL", "FIRST", "FLAME", "FLASH",
    "FLEET", "FLESH", "FLOAT", "FLOOD", "FLOOR", "FLOUR", "FLUID", "FOCUS", "FORCE",
    "FORTH", "FORTY", "FORUM", "FOUND", "FRAME", "FRESH", "FRONT", "FROST", "FRUIT",
    "GIANT", "GIVEN", "GLASS", "GLOBE", "GLORY", "GRACE", "GRADE", "GRAIN", "GRAND",
    "GRANT", "GRAPE", "GRASP", "GRASS", "GRAVE", "GREAT", "GREEN", "GREET", "GRIEF",
    "GUEST", "GUIDE", "HABIT", "HAPPY", "HARSH", "HAVEN", "HEART", "HEAVY", "HONOR",
    "HORSE", "HOTEL", "HOUSE", "HUMAN", "HUMOR", "IDEAL", "IMAGE", "INDEX", "INNER",
    "INPUT", "ISSUE", "JEWEL", "JOINT", "JUDGE", "JUICE", "KNIFE", "KNOCK", "LABEL",
    "LABOR", "LARGE", "LASER", "LATER", "LAUGH", "LAYER", "LEARN", "LEASE", "LEAST",
    "LEAVE", "LEGAL", "LEMON", "LEVEL", "LEVER", "LIGHT", "LIMIT", "LOCAL", "LOGIC",
    "LOOSE", "LOVER", "LOWER", "LOYAL", "LUCKY", "LUNCH", "MAGIC", "MAJOR", "MAKER",
    "MANGO", "MARCH", "MATCH", "MAYBE", "MAYOR", "MEDAL", "MEDIA", "MERCY", "MERIT",
    "METAL", "METER", "MIDST", "MIGHT", "MINER", "MINOR", "MODEL", "MONEY", "MONTH",
    "MORAL", "MOTOR", "MOUNT", "MOUSE", "MOUTH", "MOVIE", "MUSIC", "NAKED", "NERVE",
    "NEVER", "NIGHT", "NOBLE", "NOISE", "NORTH", "NOVEL", "NURSE", "OCEAN", "OFFER",
    "OFTEN", "ONION", "OPERA", "ORBIT", "ORDER", "ORGAN", "OTHER", "OUTER", "OWNER",
    "PAINT", "PANEL", "PANIC", "PAPER", "PARTY", "PATCH", "PAUSE", "PEACE", "PEACH",
    "PEARL", "PEDAL", "PHASE", "PHONE", "PHOTO", "PIANO", "PIECE", "PILOT", "PITCH",
    "PLACE", "PLAIN", "PLANE", "PLANT", "PLATE", "POINT", "POLAR", "POUND", "POWER",
    "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIZE", "PROOF", "PROUD", "PULSE",
    "PUNCH", "PUPIL", "QUEEN", "QUEST", "QUICK", "QUIET", "RADAR", "RADIO", "RANCH",
    "RANGE", "RAPID", "RATIO", "REACH", "REACT", "READY", "REALM", "REBEL", "RELAX",
    "RIVER", "ROBOT", "ROCKY", "ROUGH", "ROUND", "ROUTE", "ROYAL", "RULER", "RURAL",
    "SCALE", "SCENE", "SCENT", "SCOPE", "SCORE", "SCOUT", "SHADE", "SHAKE", "SHAME",
    "SHAPE", "SHARE", "SHARK", "SHARP", "SHEEP", "SHEET", "SHELF", "SHELL", "SHIFT",
    "SHINE", "SHIRT", "SHOCK", "SHOOT", "SHORE", "SHORT", "SIGHT", "SILK", "SILLY",
    "SKILL", "SKULL", "SLAVE", "SLEEP", "SLIDE", "SMART", "SMILE", "SMOKE", "SNAKE",
    "SOLAR", "SOLID", "SOLVE", "SOUND", "SOUTH", "SPACE", "SPARK", "SPEAK", "SPEED",
    "SPELL", "SPEND", "SPICE", "SPILL", "SPINE", "SPITE", "SPLIT", "SPOKE", "SPOON",
    "SPORT", "STAFF", "STAGE", "STAIN", "STAKE", "STAND", "STARE", "START", "STATE",
    "STEAM", "STEEL", "STEEP", "STEER", "STICK", "STIFF", "STILL", "STOCK", "STONE",
    "STOOL", "STORM", "STORY", "STRIP", "STUDY", "STUFF", "SUGAR", "SUITE", "SUPER",
    "SWEET", "SWIFT", "SWORD", "TABLE", "TASTE", "TEETH", "THANK", "THEME", "THICK",
    "THING", "THINK", "THIRD", "TIGER", "TITLE", "TOOTH", "TOPIC", "TOTAL", "TOUCH",
    "TOUGH", "TOWER", "TRACK", "TRADE", "TRAIL", "TRAIN", "TRAIT", "TREND", "TRIAL",
    "TRIBE", "TRICK", "TRUCK", "TRULY", "TRUNK", "TRUST", "TRUTH", "TWICE", "UNCLE",
    "UNDER", "UNION", "UNITY", "UPPER", "UPSET", "URBAN", "USAGE", "VALID", "VALUE",
    "VALVE", "VAPOR", "VAULT", "VENUE", "VERSE", "VIDEO", "VIRAL", "VIRUS", "VISIT",
    "VITAL", "VOICE", "VOTER", "WASTE", "WATCH", "WATER", "WHEAT", "WHEEL", "WHERE",
    "WHICH", "WHILE", "WHITE", "WHOLE", "WIDOW", "WIDTH", "WOMAN", "WORLD", "WORRY",
    "WORTH", "WOUND", "WRIST", "WRITE", "WRONG", "YIELD", "YOUTH", "ZEBRA"
]

WORDS_6 = [
    "FRIEND", "SPRING", "SUMMER", "WINTER", "FLOWER", "GARDEN", "CASTLE", "DRAGON",
    "KNIGHT", "BEAUTY", "SILENT", "PURPLE", "YELLOW", "ORANGE", "SHADOW", "GOLDEN",
    "SILVER", "MASTER", "WINNER", "PLAYER", "ACTION", "STREAM", "PLANET", "GALAXY",
    "CHANCE", "NATURE", "SPIRIT", "BREEZE", "SUNSET", "FOREST", "ISLAND", "CANDLE",
    "ACCEPT", "ACCESS", "ACCORD", "ACROSS", "ACTIVE", "ACTUAL", "ADVICE", "AFFORD",
    "AFRAID", "AGENCY", "AGENDA", "AGREED", "ALWAYS", "AMOUNT", "ANCHOR", "ANIMAL",
    "ANNUAL", "ANSWER", "ANYONE", "APPEAL", "APPEAR", "AROUND", "ARRIVE", "ARTIST",
    "ASPECT", "ATTACK", "ATTEND", "AUGUST", "AUTHOR", "AVENUE", "BACKED", "BAKERY",
    "BALLET", "BANANA", "BANKER", "BANNER", "BARREL", "BASKET", "BATTLE", "BEAUTY",
    "BECOME", "BEFORE", "BEHIND", "BELIEF", "BELONG", "BETTER", "BEYOND", "BISHOP",
    "BITTER", "BLANKET", "BLESS", "BORDER", "BORROW", "BOTTLE", "BOUNCE", "BRANCH",
    "BREATH", "BRIDGE", "BRIGHT", "BROKEN", "BRONZE", "BROWSE", "BUDGET", "BUFFET",
    "BULLET", "BUNDLE", "BURDEN", "BUREAU", "BUTTER", "BUTTON", "CAMERA", "CAMPUS",
    "CANCER", "CANDLE", "CANVAS", "CANYON", "CARBON", "CAREER", "CARPET", "CARROT",
    "CASINO", "CASUAL", "CAUGHT", "CEMENT", "CENTER", "CHANCE", "CHANGE", "CHANNEL",
    "CHAPEL", "CHARGE", "CHARITY", "CHARM", "CHASE", "CHEESE", "CHERRY", "CHEST",
    "CHOICE", "CHOOSE", "CHURCH", "CINEMA", "CIRCLE", "CIRCUS", "CLIENT", "CLIMATE",
    "CLINIC", "CLOSET", "CLOTH", "CLOUD", "COAST", "COFFEE", "COLD", "COLLEGE",
    "COLONY", "COLUMN", "COMBAT", "COMEDY", "COMFORT", "COMING", "COMMON", "COOKIE",
    "COPPER", "CORNER", "COSTLY", "COTTON", "COUNTY", "COUPLE", "COUSIN", "COVER",
    "CRADLE", "CRAFT", "CRATER", "CREDIT", "CRISIS", "CUSTOM", "DAMAGE", "DANGER",
    "DARING", "DEBATE", "DECADE", "DECIDE", "DEFEAT", "DEFEND", "DEGREE", "DEMAND",
    "DENTAL", "DEPUTY", "DESERT", "DESIGN", "DESIRE", "DETAIL", "DETECT", "DEVICE",
    "DIFFER", "DINNER", "DIRECT", "DOCTOR", "DOLLAR", "DOMAIN", "DONATE", "DOUBLE",
    "DRAGON", "DRAWER", "DREAM", "DRIVEN", "DRIVER", "DURING", "EAGLE", "EARTH",
    "EASILY", "EDITOR", "EFFECT", "EFFORT", "EIGHTH", "EITHER", "ELEVEN", "EMPIRE",
    "ENERGY", "ENGAGE", "ENGINE", "ENOUGH", "ENSURE", "ENTIRE", "ENTITY", "ESCAPE",
    "ESTATE", "ETHICS", "EXCEED", "EXCEPT", "EXCUSE", "EXPAND", "EXPECT", "EXPERT",
    "EXPORT", "EXTENT", "FABRIC", "FACTOR", "FAMILY", "FAMOUS", "FARMER", "FATHER",
    "FELLOW", "FEMALE", "FIGURE", "FINGER", "FINISH", "FLIGHT", "FLOWER", "FLYING",
    "FOLLOW", "FORBID", "FOREST", "FORGET", "FORMAL", "FORMAT", "FORMER", "FOSTER",
    "FOURTH", "FREEZE", "FRIEND", "FUTURE", "GALAXY", "GARAGE", "GARDEN", "GARLIC",
    "GATHER", "GENTLE", "GERMAN", "GLOBAL", "GOLDEN", "GOSPEL", "GOVERN", "GROUND",
    "GROWTH", "GUITAR", "HAMMER", "HANDLE", "HAPPEN", "HARBOR", "HARDLY", "HATRED",
    "HAZARD", "HEALTH", "HEAVEN", "HEIGHT", "HELMET", "HEROIC", "HIDDEN", "HOLDER",
    "HONEST", "HONOR", "HORROR", "HUNGER", "HUNTER", "HURRY", "HUSBAND", "IGNORE",
    "IMPACT", "IMPORT", "INCOME", "INDEED", "INFANT", "INFORM", "INSECT", "INSIDE",
    "INTEND", "INVEST", "INVITE", "ISLAND", "JACKET", "JERSEY", "JOCKEY", "JUNGLE",
    "JUNIOR", "KEEPER", "KIDNEY", "KILLER", "KISS", "KITTEN", "KNIGHT", "LABELED",
    "LADDER", "LANDED", "LAPTOP", "LATTER", "LAUNCH", "LAWYER", "LEADER", "LEAGUE",
    "LEAP", "LEGACY", "LEGEND", "LEMON", "LESSON", "LETTER", "LIGHT", "LIKELY",
    "LIMITED", "LIQUID", "LITTLE", "LIVING", "LOCATE", "LOCKER", "LONELY", "LOOSE",
    "LOVELY", "LUXURY", "MAGNET", "MAIDEN", "MAINLY", "MAKEUP", "MANAGE", "MANNER",
    "MANUAL", "MARBLE", "MARGIN", "MARKET", "MASTER", "MATTER", "MATURE", "MEADOW",
    "MEDAL", "MEDIUM", "MEMBER", "MEMORY", "MENTOR", "METHOD", "MIDDLE", "MIGHTY",
    "MINUTE", "MIRROR", "MISERY", "MOBILE", "MODERN", "MODEST", "MOMENT", "MONKEY",
    "MONSTER", "MORAL", "MORTAL", "MOTHER", "MOTION", "MOTIVE", "MOUNTAIN", "MUSEUM",
    "MUTUAL", "MYSELF", "NATION", "NATIVE", "NATURE", "NEEDLE", "NEPHEW", "NORMAL",
    "NOTICE", "NOVEL", "NUMBER", "OBJECT", "OBTAIN", "OFFICE", "OFFSET", "ONLINE",
    "OPTION", "ORANGE", "ORIGIN", "OUTPUT", "OXYGEN", "PACKET", "PALACE", "PARADE",
    "PARENT", "PARISH", "PARKED", "PARROT", "PARTLY", "PATENT", "PATROL", "PATRON",
    "PAVEMENT", "PAYMENT", "PEANUT", "PENCIL", "PEOPLE", "PEPPER", "PERIOD", "PERMIT",
    "PERSON", "PHRASE", "PICKET", "PILLOW", "PIRATE", "PLANET", "PLASTIC", "PLATE",
    "PLAYER", "PLENTY", "POCKET", "POETRY", "POLICE", "POLICY", "POLITE", "POSTAL",
    "POSTER", "POTATO", "POWDER", "PRAISE", "PRAYER", "PREFER", "PRETTY", "PRIEST",
    "PRINCE", "PRISON", "PROFIT", "PROMPT", "PROPER", "PUBLIC", "PUNISH", "PUPIL",
    "PURPLE", "PURPOSE", "PURSUIT", "PUZZLE", "RABBIT", "RADIUS", "RANDOM", "RATING",
    "REASON", "RECIPE", "RECORD", "REDUCE", "REFORM", "REFUGE", "REFUND", "REFUSE",
    "REGION", "REGRET", "RELIEF", "REMAIN", "REMEDY", "REMIND", "REMOVE", "REPAIR",
    "REPEAT", "REPORT", "RESCUE", "RESIGN", "RESIST", "RESORT", "RESULT", "RETAIL",
    "RETURN", "REVEAL", "REVIEW", "REWARD", "RHYTHM", "RIBBON", "RIDDLE", "RITUAL",
    "ROCKET", "ROLLER", "RUBBER", "RULER", "RUNNER", "SADDLE", "SAFETY", "SAILOR",
    "SALARY", "SALMON", "SAMPLE", "SANDAL", "SAUCE", "SAVING", "SCANDAL", "SCARE",
    "SCHEME", "SCHOOL", "SCIENCE", "SCREEN", "SCRIPT", "SEARCH", "SEASON", "SECOND",
    "SECRET", "SECTOR", "SECURE", "SELDOM", "SELECT", "SELLER", "SENIOR", "SENSOR",
    "SERIES", "SERMON", "SERVER", "SETTLE", "SEVENTH", "SEVERE", "SHADOW", "SHIELD",
    "SHRINE", "SIGNAL", "SILENT", "SILVER", "SIMPLE", "SINCERE", "SINGLE", "SISTER",
    "SKETCH", "SLIDER", "SMOOTH", "SOCCER", "SOCIAL", "SOCKET", "SODIUM", "SOLAR",
    "SOLDIER", "SORROW", "SOURCE", "SOVIET", "SPEECH", "SPIDER", "SPIRIT", "SPLASH",
    "SPRING", "SQUARE", "STABLE", "STATUE", "STREAM", "STREET", "STRESS", "STRIKE",
    "STRING", "STROKE", "STRONG", "STUDIO", "SUBMIT", "SUBWAY", "SUDDEN", "SUMMER",
    "SUMMIT", "SUNSET", "SUPERB", "SUPPER", "SUPPLY", "SURELY", "SURVEY", "SWITCH",
    "SYMBOL", "SYSTEM", "TABLET", "TACKLE", "TAILOR", "TALENT", "TARGET", "TARIFF",
    "TEMPLE", "TENANT", "TENDER", "TENNIS", "TERROR", "THANKS", "THEORY", "THIRST",
    "THIRTY", "THREAD", "THREAT", "THRILL", "TIMBER", "TIMING", "TISSUE", "TOBACCO",
    "TOMATO", "TONGUE", "TOWARD", "TRADER", "TRAGIC", "TRAVEL", "TREATY", "TRENDY",
    "TRIBAL", "TROPHY", "TUNNEL", "TURKEY", "TWELVE", "TWENTY", "TYPICAL", "UNABLE",
    "UNIQUE", "UNITED", "UNLESS", "UNLIKE", "UPDATE", "UPWARD", "URGENT", "VACUUM",
    "VALLEY", "VALUED", "VANISH", "VECTOR", "VELVET", "VESSEL", "VICTIM", "VICTOR",
    "VIEWER", "VIOLET", "VIRTUE", "VISION", "VISUAL", "VOYAGE", "WAITER", "WALLET",
    "WALNUT", "WARRIOR", "WEALTH", "WEAPON", "WEEKLY", "WEIGHT", "WINDOW", "WINNER",
    "WINTER", "WISDOM", "WIZARD", "WONDER", "WOODEN", "WORKER", "WORTHY", "WRITER",
    "YELLOW", "YOGURT", "ZODIAC"
]

def check_guess_colors(guess: str, secret: str):
    n = len(secret)
    result = ["🟥"] * n
    secret_chars = list(secret)
    guess_chars = list(guess)

    # 1. Green matches (exact place)
    for i in range(n):
        if guess_chars[i] == secret_chars[i]:
            result[i] = "🟩"
            secret_chars[i] = None
            guess_chars[i] = None

    # 2. Orange matches (exists but wrong place)
    for i in range(n):
        if guess_chars[i] is not None and guess_chars[i] in secret_chars:
            result[i] = "🟧"
            secret_chars[secret_chars.index(guess_chars[i])] = None

    return "".join(result)

def format_board(game):
    lines = []
    lines.append("<blockquote><b>WordSeek</b>")
    lines.append(f"<i>{game['size']}-letter mode • {len(game['history'])}/30</i>\n")

    for h in game["history"]:
        lines.append(f"{h['colors']}   <b>{h['word']}</b>")

    lines.append("</blockquote>")
    return "\n".join(lines)

async def auto_stop_timer(client: Client, chat_id: int, duration_sec: int, secret_word: str):
    await asyncio.sleep(duration_sec)
    if chat_id in GAMES and GAMES[chat_id]["secret"] == secret_word:
        game = GAMES.pop(chat_id)
        try:
            await client.send_message(
                chat_id,
                f"<blockquote>⌛ <b>TIME UP!</b>\n"
                f"🎯 <b>The secret word was:</b> <code>{game['secret']}</code></blockquote>"
            )
        except Exception:
            pass

@Client.on_message(filters.command(["new", "new4", "new5", "new6"], prefixes=["/", "."]))
async def start_wordseek(client: Client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if chat_id in GAMES:
        remaining = int(GAMES[chat_id]["end_time"] - time.time())
        if remaining > 0:
            await message.reply(
                f"<blockquote>⚠️ Game already running! Time remaining: <b>{remaining}s</b></blockquote>",
                quote=True
            )
            return

    # Default .new is new5
    if cmd in ["new", "new5"]:
        size = 5
        minutes = 8
        secret = random.choice(WORDS_5)
    elif cmd == "new4":
        size = 4
        minutes = 5
        secret = random.choice(WORDS_4)
    else:  # new6
        size = 6
        minutes = 10
        secret = random.choice(WORDS_6)

    duration_sec = minutes * 60
    end_time = time.time() + duration_sec

    GAMES[chat_id] = {
        "size": size,
        "secret": secret,
        "end_time": end_time,
        "history": [],
        "max_guesses": 30
    }

    asyncio.create_task(auto_stop_timer(client, chat_id, duration_sec, secret))

    # Clean short start notice
    await message.reply(f"<blockquote>🎮 <b>Started new{size} wordseek!</b></blockquote>")

# Chat listener for WordSeek guesses
@Client.on_message(filters.group & filters.text & ~filters.bot, group=12)
async def wordseek_guess_checker(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES:
        return

    guess = message.text.strip().upper()

    # Skip commands or multi-word sentences
    if guess.startswith(("/", ".", "!", "#")) or len(guess.split()) > 1:
        return

    game = GAMES[chat_id]
    size = game["size"]

    if len(guess) != size or not guess.isalpha():
        return

    # Check against valid dictionary
    valid_pool = WORDS_4 if size == 4 else (WORDS_5 if size == 5 else WORDS_6)
    if guess not in valid_pool:
        await message.reply(
            f"<blockquote><b>WordSeek</b>\n<code>{message.text.strip()}</code> is not a valid {size}-letter word.</blockquote>",
            quote=True
        )
        return

        secret = game["secret"]
    colors = check_guess_colors(guess, secret)

    game["history"].append({
        "word": guess,
        "colors": colors,
        "user": message.from_user.first_name
    })

    board_text = format_board(game)

    # WIN CHECK
    if guess == secret:
        GAMES.pop(chat_id)
        mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        win_text = (
            f"{board_text}\n\n"
            f"<blockquote>🎉 <b>CONGRATULATIONS!</b>\n"
            f"🏆 {mention} won! The word was <code>{secret}</code> 🥳</blockquote>"
        )
        await message.reply(win_text, quote=True)
        return

    # MAX GUESS REACHED
    if len(game["history"]) >= game["max_guesses"]:
        GAMES.pop(chat_id)
        lose_text = (
            f"{board_text}\n\n"
            f"<blockquote>⌛ <b>GAME OVER!</b> Max guesses reached.\n"
            f"🎯 <b>Correct word was:</b> <code>{secret}</code></blockquote>"
        )
        await message.reply(lose_text, quote=True)
        return

    await message.reply(board_text, quote=True)
    
