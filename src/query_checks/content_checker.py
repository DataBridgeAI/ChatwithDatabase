# query_checks/content_checker.py
import re
from typing import Optional
import pandas as pd
from snorkel.labeling import labeling_function

# Check if Detoxify is available
try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False

# Reusable Detection Functions
def detect_probe(text: str, probe_pattern: str, keywords: str) -> bool:
    """Detect probing questions with specific keywords."""
    return bool(re.search(probe_pattern, text) and re.search(keywords, text))

def detect_keywords(text: str, keywords: str) -> bool:
    """Detect explicit mentions of specific keywords."""
    return bool(re.search(keywords, text))

def detect_bias(text: str, groups: str, bias_pattern: str) -> bool:
    """Detect bias or stereotypes with specific groups and bias terms."""
    return bool(re.search(groups, text) and re.search(bias_pattern, text))

# Detoxify Integration
def analyze_with_detoxify(text: str) -> dict:
    """Use Detoxify to analyze text if available, return empty dict otherwise."""
    if DETOXIFY_AVAILABLE:
        return Detoxify('original').predict(text)
    return {}

def is_sensitive(text: str, detoxify_results: dict = None) -> bool:
    """
    Check if text is sensitive (religion, gender, race, etc.).
    Modular and reusable.
    """
    text = text.lower()
    detoxify_results = detoxify_results or analyze_with_detoxify(text)
    if detoxify_results:
        # Detoxify-based detection for religion, gender, etc.
        return (detoxify_results.get('toxicity', 0) > 0.7 or
                detoxify_results.get('identity_attack', 0) > 0.5 or
                detoxify_results.get('insult', 0) > 0.5)
    else:
        # Fallback: Structural detection for probing questions
        probe_pattern = r'\b(what|which|who|why|how|is|are|best|worst|better|worse)\b'
        relational_clue = r'\b(of|in|for|about|than)\b'
        return (re.search(probe_pattern, text) and re.search(relational_clue, text))

def is_harmful(text: str, detoxify_results: dict = None) -> bool:
    """
    Check if text suggests harmful intent (terrorism, violence).
    Modular and reusable.
    """
    text = text.lower()
    detoxify_results = detoxify_results or analyze_with_detoxify(text)
    if detoxify_results:
        # Detoxify-based detection for harmful intent
        return (detoxify_results.get('threat', 0) > 0.5 or
                detoxify_results.get('obscene', 0) > 0.5)
    else:
        # Fallback: Action-oriented harmful intent
        action_pattern = r'\b(how|do|make|start|plan)\b'
        harm_pattern = r'\b(war|kill|attack)\b'
        return (re.search(action_pattern, text) and re.search(harm_pattern, text))

def is_sql_command(text: str) -> bool:
    """
    Check if text resembles an SQL command.
    Modular and minimal hardcoding.
    """
    sql_pattern = r'\b[A-Z]{2,}\b'
    return re.search(sql_pattern, text) and (' ' in text or ';' in text)

# Common Patterns
PROBE_PATTERN = r'\b(what|which|who|why|how|is|are|do|differ|wrong|best|better|worse|superior|bad)\b'
BIAS_PATTERN = r'\b(better|worse|best|worst|superior|weak|strong|lazy|smart|stupid|good|bad|' \
               r'hate|wrong|dangerous|rich|poor|aggressive|useless|differ|problem|judge)\b'

# Category-Specific Keywords with Expanded Lists

# Region/Nationality
REGION_KEYWORDS = r'\b(country|nation|americans|russians|chinese|indians|mexicans|japan|canadians|brazil|germans|' \
                  r'middle east|africa|asia|europe|pakistan|india|china|america|british|french|italians|spanish|' \
                  r'australians|koreans|vietnamese|turks|egyptians|saudis|iranians|iraqis|syrians|afghans|continent|' \
                  r'region|nationality|english|scottish|irish|welsh|dutch|swedish|norwegian|danish|finnish|greek|' \
                  r'polish|ukrainians|romanians|hungarians|czechs|slovaks|bulgarians|thai|malaysians|indonesians|' \
                  r'filipinos|singaporeans|south africans|nigerians|kenyans|moroccans|algerians|tunisians|libyans|' \
                  r'sudanese|ethiopians|somali|ghanaian|zimbabwean|colombians|argentinians|peruvians|chileans|' \
                  r'venezuelans|cubans|jamaicans)\b'
REGION_GROUPS = r'\b(americans|russians|chinese|indians|mexicans|japan|canadians|brazil|germans|pakistan|india|' \
                r'china|america|british|french|italians|spanish|australians|koreans|vietnamese|turks|egyptians|' \
                r'saudis|iranians|iraqis|syrians|afghans|english|scottish|irish|welsh|dutch|swedish|norwegian|' \
                r'danish|finnish|greek|polish|ukrainians|romanians|hungarians|czechs|slovaks|bulgarians|thai|' \
                r'malaysians|indonesians|filipinos|singaporeans|south africans|nigerians|kenyans|moroccans|' \
                r'algerians|tunisians|libyans|sudanese|ethiopians|somali|ghanaian|zimbabwean|colombians|' \
                r'argentinians|peruvians|chileans|venezuelans|cubans|jamaicans)\b'

# Religion
RELIGION_KEYWORDS = r'\b(religion|muslims|christians|jews|hindus|buddhists|islam|christianity|atheism|faith|' \
                    r'worship|sikhs|jainism|taoism|shinto|pagan|agnostic|spiritual|prayer|church|mosque|temple|' \
                    r'synagogue|god|allah|buddha|jesus|vishnu|belief|sect|cult|preach|holy|sacred|divine|pastor|' \
                    r'priest|imam|rabbi|monk|nun|scripture|bible|quran|torah|vedas|guru|meditation|ritual|heaven|' \
                    r'hell|sin|salvation|reincarnation|karma|nirvana|pilgrimage|fasting|prophet|saint|deity|' \
                    r'missionary|orthodox|catholic|protestant|sunni|shia|sufi|evangelical|mormon|jehovah)\b'
RELIGION_GROUPS = r'\b(muslims|christians|jews|hindus|buddhists|sikhs|jains|taoists|shintoists|pagans|agnostics|' \
                  r'atheists|catholics|protestants|sunnis|shias|sufis|evangelicals|mormons|jehovahs)\b'

# Racial/Ethnicity
RACIAL_KEYWORDS = r'\b(race|skin|black|white|asian|latino|hispanic|indians|native|americans|africans|ethnicity|' \
                  r'arab|caucasian|mixed|biracial|indigenous|tribal|aboriginal|brown|yellow|color|heritage|' \
                  r'ancestry|lineage|roots|minority|multiracial|negro|mulatto|creole|polynesian|melanesian|' \
                  r'micronesian|pacific islander|inuit|eskimo|sami|berber|kurd|turkmen|uzbek|kazakh|mongolian|' \
                  r'tibetan|hmong|maori|samoan|tongan|gypsy|roma|traveller|diaspora|clan)\b'
RACIAL_GROUPS = r'\b(black|white|asian|latino|hispanic|indians|native|americans|africans|arab|caucasian|' \
                r'indigenous|aboriginal|negro|mulatto|creole|polynesian|melanesian|micronesian|pacific islander|' \
                r'inuit|eskimo|sami|berber|kurd|turkmen|uzbek|kazakh|mongolian|tibetan|hmong|maori|samoan|' \
                r'tongan|gypsy|roma|traveller)\b'

# Gender/Sexuality
GENDER_KEYWORDS = r'\b(women|men|gender|sex|sexual|trans|nonbinary|gay|lesbian|queer|bisexual|pansexual|asexual|' \
                  r'arousal|orientation|identity|transgender|cisgender|intersex|female|male|feminism|masculinity|' \
                  r'patriarchy|matriarchy|hormone|genital|pregnancy|abortion|lgbt|lgbtq|straight|heterosexual|' \
                  r'homosexual|polyamory|virgin|chastity|libido|erection|orgasm|masturbation|porn|prostitute|' \
                  r'brothel|seduction|flirt|romance|marriage|divorce|adultery|polygamy|monogamy|celibate|' \
                  r'feminist|misogyny|chauvinism|androgynous|effeminate|butch|femme|drag|crossdress)\b'
GENDER_GROUPS = r'\b(women|men|trans|nonbinary|gay|lesbian|queer|bisexual|pansexual|asexual|transgender|' \
                r'cisgender|intersex|female|male|heterosexual|homosexual)\b'

# Politics
POLITICS_KEYWORDS = r'\b(party|democracy|liberals|conservatives|socialists|communism|republicans|democrats|' \
                    r'trump|biden|politics|election|vote|government|policy|president|prime minister|congress|' \
                    r'parliament|senate|dictator|monarchy|anarchy|fascism|capitalism|marxism|libertarian|' \
                    r'nationalism|patriotism|citizen|union|law|constitution|bill|tax|welfare|campaign|' \
                    r'lobby|activism|protest|reform|revolution|regime|diplomacy|embassy|treaty|sanction|' \
                    r'corruption|scandal|ideology|left|right|center|radical|moderate)\b'

# Terrorism/Violence
TERRORISM_KEYWORDS = r'\b(war|kill|attack|bomb|terrorists|weapon|destroy|terrorism|coup|revolution|assault|' \
                     r'murder|violence|riot|massacre|genocide|execution|shoot|stab|explode|arson|hostage|' \
                     r'kidnap|abduct|torture|threat|bloodshed|battle|combat|insurgency|militia|rebel|guerilla|' \
                     r'sabotage|assassination|jihad|extremism|radicalize|detonate|gun|knife|missile|drone|' \
                     r'warfare|slaughter|mayhem|chaos|anarchy)\b'
HARM_PATTERN = r'\b(war|kill|attack|bomb|terror|terrorists|weapon|destroy|violence|hate|coup|revolution|assault|' \
               r'murder|riot|massacre|genocide|execution|shoot|stab|explode|arson|hostage|kidnap|abduct|' \
               r'torture|threat|bloodshed|battle|combat|insurgency|rebel|sabotage|assassination|jihad|' \
               r'extremism|radicalize|detonate|gun|knife|missile|drone|warfare|slaughter|mayhem|chaos)\b'
ACTION_PATTERN = r'\b(how|do|make|start|plan|tell|attack|destroy|judge|execute|shoot|stab|bomb|kill|threaten|' \
                 r'torture|abduct|assassinate|detonate|riot|rebel|sabotage)\b'

# Age
AGE_KEYWORDS = r'\b(age|old|millennials|boomers|gen z|youth|elderly|teenagers|seniors|generation|child|kid|' \
               r'baby|infant|toddler|adolescent|adult|mature|middle-aged|retiree|senile|young|prime|newborn|' \
               r'juvenile|minor|grownup|aging|wrinkle|puberty|menopause|grandparent|teen|twenties|thirties|' \
               r'forties|fifties|sixties|seventies|eighties|nineties|centenarian)\b'

# Miscellaneous Social Categories
MISC_GROUPS = r'\b(fat|poor|rich|disabled|smart|dumb|tall|ugly|beauty|mental|illness|looks|thin|obese|skinny|' \
              r'wealthy|broke|homeless|crippled|blind|deaf|mute|insane|crazy|genius|idiot|short|handsome|' \
              r'pretty|attractive|unattractive|sick|healthy|fit|weak|strong|lazy|active|employed|unemployed|' \
              r'addict|drunk|sober|scarred|tattooed|pierced)\b'

# Obscene Language
OBSCENE_PATTERN = r'\b(fuck|fukkard|fucked|fucking|shit|shite|shitted|shitting|bitch|bitches|asshole|arsehole|' \
                  r'kill|die|damn|damned|cunt|cock|dick|prick|pussy|bastard|whore|slut|twat|wanker|jerkoff|' \
                  r'motherfucker|ass|arse|bullshit|piss|pissed|crappy|suck|sucks|balls|nut sack|douche|' \
                  r'faggot|nigger|retard|cum|jizz|semen|poop|fart|pee|friggin|frigging|crap|bollocks|tits)\b'

# Labeling Functions
# Region/Nationality
@labeling_function()
def lf_region_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, REGION_KEYWORDS):
        return "This query involves a regional or national topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_region_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, REGION_KEYWORDS):
        return "This query mentions a region or nationality not relevant to the dataset. Please focus on data-related queries."
    return None

@labeling_function()
def lf_region_bias(row):
    text = row["text"].lower()
    if detect_bias(text, REGION_GROUPS, BIAS_PATTERN):
        return "This query suggests bias about a region or nationality, which is inappropriate for this dataset. Please rephrase."
    return None

# Religion
@labeling_function()
def lf_religion_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, RELIGION_KEYWORDS):
        return "This query involves a religious topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_religion_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, RELIGION_KEYWORDS):
        return "This query mentions a religious topic not relevant to the dataset. Please focus on data-related queries."
    return None

@labeling_function()
def lf_religion_bias(row):
    text = row["text"].lower()
    if detect_bias(text, RELIGION_GROUPS, BIAS_PATTERN):
        return "This query suggests bias about a religion, which is inappropriate for this dataset. Please rephrase."
    return None

# Racial/Ethnicity
@labeling_function()
def lf_racial_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, RACIAL_KEYWORDS):
        return "This query involves a racial or ethnic topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_racial_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, RACIAL_KEYWORDS):
        return "This query mentions a racial or ethnic topic not relevant to the dataset. Please focus on data-related queries."
    return None

@labeling_function()
def lf_racial_bias(row):
    text = row["text"].lower()
    if detect_bias(text, RACIAL_GROUPS, BIAS_PATTERN):
        return "This query suggests bias about race or ethnicity, which is inappropriate for this dataset. Please rephrase."
    return None

# Gender
@labeling_function()
def lf_gender_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, GENDER_KEYWORDS):
        return "This query involves a gender or sexuality topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_gender_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, GENDER_KEYWORDS):
        return "This query mentions a gender or sexuality topic not relevant to the dataset. Please focus on data-related queries."
    return None

@labeling_function()
def lf_gender_bias(row):
    text = row["text"].lower()
    if detect_bias(text, GENDER_GROUPS, BIAS_PATTERN):
        return "This query suggests bias about gender or sexuality, which is inappropriate for this dataset. Please rephrase."
    return None

# Politics
@labeling_function()
def lf_politics_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, POLITICS_KEYWORDS):
        return "This query involves a political topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_politics_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, POLITICS_KEYWORDS):
        return "This query mentions a political topic not relevant to the dataset. Please focus on data-related queries."
    return None

# Terrorism
@labeling_function()
def lf_terrorism_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, TERRORISM_KEYWORDS):
        return "This query relates to violence or terrorism, which is inappropriate for this dataset. I can't assist."
    return None

@labeling_function()
def lf_harmful_intent(row):
    text = row["text"].lower()
    if re.search(ACTION_PATTERN, text) and re.search(HARM_PATTERN, text):
        return "This query suggests harmful intent (e.g., violence, hate), which is inappropriate for this dataset. I can't assist."
    return None

# Other Categories (Age, Miscellaneous, Obscene, SQL)
@labeling_function()
def lf_age_probe(row):
    text = row["text"].lower()
    if detect_probe(text, PROBE_PATTERN, AGE_KEYWORDS):
        return "This query involves an age-related topic irrelevant to the dataset. Please ask a data-related question."
    return None

@labeling_function()
def lf_age_keywords(row):
    text = row["text"].lower()
    if detect_keywords(text, AGE_KEYWORDS):
        return "This query mentions an age-related topic not relevant to the dataset. Please focus on data-related queries."
    return None

@labeling_function()
def lf_misc_bias(row):
    text = row["text"].lower()
    if detect_bias(text, MISC_GROUPS, BIAS_PATTERN):
        return "This query suggests bias about a social group (e.g., wealth, ability), which is inappropriate for this dataset. Please rephrase."
    return None

@labeling_function()
def lf_obscene_language(row):
    text = row["text"].lower()
    if re.search(OBSCENE_PATTERN, text):
        return "This query contains inappropriate language not suitable for this dataset. Please rephrase."
    return None

@labeling_function()
def lf_sql_injection(row):
    text = row["text"].upper()
    sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]
    if any(word in text for word in sql_blacklist):
        return "This query contains restricted SQL operations. Please use valid data queries."
    return None

# New functions for integration with Detoxify
def detect_sensitive_content(text: str) -> Optional[str]:
    """Detect and respond to sensitive content using Detoxify."""
    results = analyze_with_detoxify(text)
    if results and is_sensitive(text, results):
        return "🤝 This query might touch on a sensitive topic (e.g., religion, gender). Let's focus on neutral questions."
    return None

def block_inappropriate_query(text: str) -> Optional[str]:
    """Block queries with harmful intent using Detoxify."""
    results = analyze_with_detoxify(text)
    if results and is_harmful(text, results):
        return "This query suggests harmful intent (e.g., terrorism, violence). I can't assist with that."
    return None

def check_sql_safety(text: str) -> Optional[str]:
    """Ensure SQL safety using improved pattern matching."""
    if is_sql_command(text):
        return "Restricted SQL operation detected."
    return None

# Centralized Sensitivity Filter - Combined approach
def sensitivity_filter(user_query: str) -> Optional[str]:
    """
    Check query and return specific comments if inappropriate using both 
    pattern-based detection and Detoxify (when available).
    """
    # First try Detoxify-based detection (if available)
    if DETOXIFY_AVAILABLE:
        # Check with Detoxify first for more accurate detection
        detoxify_checks = [
            detect_sensitive_content,
            block_inappropriate_query,
            check_sql_safety
        ]
        
        for check in detoxify_checks:
            result = check(user_query)
            if result:
                return result
    
    # Fall back to pattern-based labeling functions
    lfs = [
        # Prioritize bias detection, then probes, then keywords
        lf_region_bias, lf_region_probe, lf_region_keywords,
        lf_religion_bias, lf_religion_probe, lf_religion_keywords,
        lf_racial_bias, lf_racial_probe, lf_racial_keywords,
        lf_gender_bias, lf_gender_probe, lf_gender_keywords,
        lf_politics_probe, lf_politics_keywords,
        lf_terrorism_probe, lf_harmful_intent,
        lf_age_probe, lf_age_keywords,
        lf_misc_bias, lf_obscene_language, lf_sql_injection
    ]
    df = pd.DataFrame([{"text": user_query}])
    
    # Return the first non-None comment
    for lf in lfs:
        result = lf(df.iloc[0])
        if result:
            return result
    return None
