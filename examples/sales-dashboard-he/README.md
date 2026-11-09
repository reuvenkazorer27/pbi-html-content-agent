# דוגמה עובדת: דשבורד מכירות RTL מורכב (composite) על בד 1280×720

דוגמה מלאה ל-pattern B (composite) עם שורת KPI עליונה, פריסה צפופה ומסודרת בלי חללים מתים, ורכיבים שמנצלים את מה ש-HTML יכול מעבר למובנה: variance בדגנ"ח IBCS, dumbbell, כרטיסי חריגות עם פעולה מומלצת, stage tracker לתהליך, narrative מחושב עם ספארקליין בתוך המשפט, scorecard ובאנר מצב-סינון - לצד סלייסר נטיבי ותפריט צד מימין עם כפתורי ניווט נטיביים שקופים.

**מהדורה:** HTML Content Secure מספיקה לכל מה שכאן (אין סקריפטים ואין משאבים חיצוניים), ולכן הדשבורד גם נכנס ל-export ל-PDF/PowerPoint.
**מצב אימות:** לא הורץ ב-Power BI. מבוסס על תיעוד 2.0 בלבד. להריץ את `../../checklists/validation.md` לפני שימוש.

## פריסת העמוד (כל המספרים בפיקסלים, כפולות של 8)

רקע דף: `#F4F7FA` (Ocean BI `bg`). לכל ויזואלי ה-HTML: Effects > Background/Border/Shadow כבויים. רוחב שמיש 1232 (margins של 24), תפריט 200 בימין (x=1056), אזור תוכן 24..1040 ברוחב 1016, gutters של 8 בלבד - ככה הפריסה נשארת צפופה.

| # | תפקיד | סוג | x | y | w | h | z |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Header | HTML Content: `HTML Header` | 24 | 16 | 1232 | 56 | 1 |
| 2 | תפריט צד | HTML Content: `HTML Side Menu` | 1056 | 80 | 200 | 624 | 1 |
| 3 | כפתור ניווט: מכירות | Native blank button (שקוף) | מעל פריט התפריט הראשון | | | | 3 |
| 4 | כפתור ניווט: מוצרים | Native blank button (שקוף) | מעל פריט התפריט השני | | | | 3 |
| 5 | KPI: הכנסות | HTML Content: `HTML KPI Trend - Revenue` | 24 | 80 | 248 | 120 | 1 |
| 6 | KPI: הזמנות | HTML Content: `HTML KPI Trend - Orders` | 280 | 80 | 248 | 120 | 1 |
| 7 | KPI: סל ממוצע | HTML Content: `HTML KPI Trend - Avg Basket` | 536 | 80 | 248 | 120 | 1 |
| 8 | KPI: רווח גולמי | HTML Content: `HTML KPI Trend - Gross Profit` | 792 | 80 | 248 | 120 | 1 |
| 9 | באנר מצב-סינון | HTML Content: `HTML Filter Banner` | 24 | 208 | 688 | 40 | 1 |
| 10 | סלייסר שנה | Native slicer על `Date[Year]` (סגנון אריחים) | 728 | 208 | 312 | 40 | 1 |
| 11 | variance IBCS | HTML Content: `HTML Variance Row` + Context=`Sales[Category]` | 24 | 256 | 496 | 256 | 1 |
| 12 | כרטיסי חריגות | HTML Content: `HTML Exception Row` + Context=`Sales[Category]` | 536 | 256 | 504 | 160 | 1 |
| 13 | stage tracker | HTML Content: `HTML Stage Tracker` | 536 | 424 | 504 | 88 | 1 |
| 14 | narrative | HTML Content: `HTML Narrative - Revenue` | 24 | 520 | 1016 | 48 | 1 |
| 15 | scorecard: קטגוריות | HTML Content: `HTML Scorecard Row` + Context=`Sales[Category]` | 24 | 576 | 496 | 128 | 1 |
| 16 | dumbbell: השנה מול שנה שעברה | HTML Content: `HTML Dumbbell Row` + Context=`Sales[Category]` | 536 | 576 | 504 | 128 | 1 |

חשבון הרוחב: 4 כרטיסי KPI של 248 + 3 gutters של 8 = 1016. כל שורה: 496 + 8 + 504 = 1008, ועוד gutter של 8 לתפריט. חשבון הגובה: KPI מסתיימת ב-200, סינון 208-248, אמצע 256-512, narrative 520-568, שורה תחתונה 576-704. ה-KPI תמיד בשורה הראשונה מתחת ל-header, ואין אזור ריק מעל gutter אחד.

## מה "עובד" בדשבורד הזה (במדויק)

- סלייסר השנה (נטיבי) מסנן את כל ויזואלי ה-HTML. תמיד עובד, בלי הגדרה. באנר מצב-הסינון משקף אותו דרך `SELECTEDVALUE`/`ISFILTERED`.
- הוויזואלים עם Context (11, 14, 15, 16) מגיבים לכל סינון בדף, וקליק ימני פותח context menu כולל drillthrough אם קיים עמוד drillthrough. אם מפעילים Cross-filtering > Enable באחד מהם, לחיצה על שורה מסננת גם את השאר.
- באנר ההתראות מחושב ב-DAX: כמה קטגוריות מתחת ליעד ואילו, עם צבע סטטוס.
- פריטי התפריט מנווטים בין עמודים דרך כפתורים נטיביים שקופים שמונחים מעליהם (שורות 3-4 בטבלה). ה-HTML עצמו לא מנווט.
- ייצוא ל-PDF: עובד כי כל הוויזואלים הם Secure.

## צעדי בנייה ב-Desktop

1. ודאו שהדף הוא 16:9 בגודל 1280×720 (Format page > Canvas settings).
2. התקינו את HTML Content Secure מ-AppSource (חפשו "HTML Content Secure").
3. צרו טבלת measures בשם `_HTML` והדביקו לתוכה את ה-measures מ-`measures.dax` (התאימו שמות טבלאות/עמודות למודל שלכם).
4. לכל שורה בטבלת הפריסה: הוסיפו ויזואל HTML Content, קשרו את ה-measure ל-Values (ואת עמודת ה-Context איפה שמצוין), הגדירו מיקום וגודל לפי הטבלה.
5. הדביקו את ה-CSS של כל רכיב ל-Stylesheet של אותו ויזואל (או אחד משותף דרך fx על measure).
6. הניחו את כפתורי הניווט השקופים מעל פריטי התפריט (Insert > Buttons > Blank > Action > Page navigation), ותעדו את המלבנים בטבלה.
7. הריצו את `../../checklists/validation.md`.

## קבצים

- `measures.dax` - כל ה-measures של הדשבורד (מעתיקים מהספרייה, מותאמים לשמות המודל של הדוגמה).
- הרכיבים המקוריים: `../../library/components/`.
