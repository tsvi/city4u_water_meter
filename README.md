# Water Consumption Data Fetcher

A utility for fetching water consumption data from the City4U API and storing it locally. This tool helps you retrieve and track your water usage information automatically.

## Features

- Interactive setup wizard for first-time users
- Proper Hebrew display for city selection
- Configuration file support to avoid repetitive credential entry
- Command-line arguments for automation and scripting
- Secure credential handling

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or PDM (Python package manager)

### Setup with PDM (recommended)

```bash
# Install PDM if you don't have it already
pip install pdm

# Install dependencies
pdm install
```

### Setup with pip

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### First-time Setup

> **Important:** For the best experience, create a permanent password in the City4U website rather than using the temporary SMS login. A permanent password allows for reliable automated access.

Run the setup wizard to configure your credentials:

```bash
pdm run python src/read_water/fetch_water_data.py --setup
```

This will guide you through:

1. Entering your City4U username and password
   - In most cases, the username is your Israeli ID number (תעודת זהות)
   - Use your permanent password, not a temporary SMS code
2. Selecting your city from a list
3. Configuring your meter number and output file location

The configuration will be saved to `~/.config/water_consumption/config.json` for future use.

### Basic Usage

Once configured, simply run:

```bash
pdm run python src/read_water/fetch_water_data.py
```

### Command-line Options

```bash
--username      Your City4U username (usually your Israeli ID number/תעודת זהות)
--password      Your City4U password (overrides config file)
--customer-id   Your City4U customer ID (overrides config file)
--meter-number  Your meter number (defaults to username if not provided)
--output        Output JSON file path
--setup         Run the setup process to create/update configuration
--debug         Enable debug logging
```

## Project Structure

```text
read_water/
├── src/
│   └── read_water/
│       ├── __init__.py
│       └── fetch_water_data.py  # Main script
├── .github/
│   └── workflows/
│       └── code-quality.yml     # GitHub CI configuration
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
└── README.md                    # This file
```

## Development

This project uses pre-commit hooks to maintain code quality. To set up the development environment:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

### Code Quality Tools

The project uses multiple tools to ensure code quality:

- **Ruff**: Fast Python linter and formatter
- **isort**: Import sorter
- **MyPy**: Type checking with strict settings
- **Pylint**: Comprehensive Python linting

These checks run automatically on commit and in GitHub Actions.

## Configuration File

The configuration file is stored at `~/.config/water_consumption/config.json` and follows this format:

```json
{
  "username": "your_id_number",  // Usually your Israeli ID number (תעודת זהות)
  "password": "your_password",   // Use permanent password from City4U website, not SMS code
  "customer_id": 12345,
  "meter_number": "your_meter_number",
  "output_file": "water_consumption_data.json"
}
```

**Note:** The password should be your permanent password created on the City4U website, not a temporary SMS code. This ensures the tool can continue to authenticate automatically.

## Supported Municipalities

The following municipalities use the City4U system and are probably supported by this tool (200+ municipalities):

> **Note:** This is an extensive list. Scroll through to find your municipality.

1. אבו סנאן
2. אבן יהודה
3. אום אל פאחם
4. אופקים
5. אור יהודה
6. אור עקיבא
7. אזור
8. אילת
9. אכסאל
10. אל בטוף
11. אל קסום
12. אלונה
13. אליכין
14. אלעד
15. אלקנה
16. אעבלין
17. אפעל
18. אפרת
19. אריאל
20. אשדוד
21. אשקלון
22. באקה אל- גרביה
23. באר טוביה
24. באר יעקב
25. באר שבע
26. בוסתן אל מרג
27. בועיינה-נוג'ידאת
28. בוקעתא
29. ביר אל מכסור
30. בית אריה
31. בית דגן
32. בית שמש
33. ביתר עילית
34. בני ברק
35. בני שמעון
36. בנימינה-גבעת עדה
37. בסמה
38. בסמת טבעון
39. בענה
40. ברנר
41. בת ים
42. ג'דיידה מכר
43. ג'וליס
44. ג'לג'וליה
45. ג'ת
46. גבעת זאב
47. גבעתיים
48. גדרה
49. גולן
50. גוש חלב
51. גזר
52. גן יבנה
53. גן רוה
54. גני תקווה
55. ג'סר אל זרקא
56. דבוריה
57. דימונה
58. דיר אל אסד
59. דרום השרון
60. הגלבוע
61. הגליל העליון
62. הערבה התיכונה
63. הר אדר
64. הר חברון
65. הרצליה
66. זכרון יעקב
67. זמר
68. זרזיר
69. חבל מודיעין
70. חדרה
71. חולון
72. חוף אשקלון
73. חוף הכרמל
74. חורה
75. חורפיש
76. חיפה
77. חצור הגלילית
78. חריש
79. טבריה
80. טובה זנגריה
81. טורעאן
82. טייבה
83. טירה
84. טירת כרמל
85. יאנוח ג'ת
86. יבנאל
87. יבנה
88. יהוד - מונוסון
89. יסוד המעלה
90. יפיע
91. יקנעם עילית
92. ירוחם
93. כאבול
94. כוכאב
95. כוכב יאיר - צור יגאל
96. כסייפה
97. כסרא סמיע
98. כעביה-טבאש
99. כפר ורדים
100. כפר יאסיף
101. כפר כנא
102. כפר מנדא
103. כפר סבא
104. כפר קרע
105. כפר שמריהו
106. כפר תבור
107. כרמיאל
108. לב השרון
109. להבים
110. לוד
111. לכיש
112. מבשרת ציון
113. מג'אר
114. מגדל
115. מגדל העמק
116. מגדל שמס
117. מגידו
118. מודיעין
119. מודיעין מכבים רעות
120. מודיעין עילית
121. מזרעה
122. מטה אשר
123. מטולה
124. מי אשקלון
125. מי הוד השרון
126. מי הרצליה
127. מי כרמל
128. מי מודיעין
129. מי עירון
130. מי ציונה
131. מי רקת
132. מים אילת
133. מיתר
134. מכבים רעות
135. מנשה
136. מעיינות
137. מעיינות אתא
138. מעיינות הדרום
139. מעיינות העמקים
140. מעיינות השרון
141. מעלה אדומים
142. מעלה אפרים
143. מעלה יוסף
144. מפעל המים כפר סבא
145. מצפה רמון
146. מרום הגליל
147. מרכז מסחרי שוהם
148. מרכז שלטון מקומי
149. משגב
150. משהד
151. נווה מדבר
152. נחף
153. נס ציונה
154. נצרת
155. נתיבות
156. נתניה
157. סאג'ור
158. סביון
159. סח'נין
160. עומר
161. עילבון
162. עין מאהל
163. עין קיניא
164. עמותת על"ה רמת גן
165. עמק הירדן
166. עמק חפר
167. עספיא
168. עפולה
169. ערד
170. ערערה
171. ערערה בנגב
172. עתלית
173. פקיעין
174. פרדס
175. פרדס חנה - כרכור
176. פרדסיה
177. פתח תקווה
178. צורן
179. צפת
180. קדומים
181. קדמת גליל
182. קלנסואה
183. קצרין
184. קרית אונו
185. קרית אתא
186. קרית ביאליק
187. קרית גת
188. קרית טבעון
189. קרית ים
190. קרית מלאכי
191. ראש העין
192. ראשון לציון
193. רחובות
194. ריינה
195. רמת גן
196. רמת הנגב
197. רמת השרון
198. רמת ישי
199. רעננה
200. שגב שלום
201. שדות נגב
202. שלומי
203. שעב
204. שער הנגב
205. שפיר
206. תאגיד מי רמת גן
207. תאגיד מים מי שמש
208. תל אביב
209. תל מונד
210. תמרה
211. תפן

## License

MIT
