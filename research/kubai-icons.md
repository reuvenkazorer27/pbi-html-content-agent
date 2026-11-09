# Kubai Icons - זיהוי, רישיון והתאמה (נבדק חי 09/11/2026)

בקשת המשתמש (10:23): "אולי תטמיע את Kubai icons ליצירת אייקונים מותאמים לkpi או תפריט צד".

## זיהוי (לא שוער - אומת)
- הריפו: https://github.com/kubai087/kubai-icons (נוצר 03/11/2026). האתר: https://icons.kubai.design/
- מסמך הרישיונות שנקרא: https://github.com/kubai087/kubai-icons/blob/master/LICENSING.md
- רישיון MIT של האייקונים: https://github.com/kubai087/kubai-icons/blob/master/LICENSE-ICONS
- רישיון ה-Skill (source-available): https://github.com/kubai087/kubai-icons/blob/master/LICENSE
- חבילת ה-SVG הסטטיים ב-npm: https://www.npmjs.com/package/kubai-icons-static
- מה זה: שני דברים באותו ריפו:
  1. **ספריית אייקונים** - אייקונים רבים (icons/) + חבילות מוכנות (packages/), כולל `kubai-icons-static` ב-npm: קבצי SVG עצמאיים לחלוטין (בלי JS, בלי CSS חיצוני), 2,871 קבצים (כולל וריאנטים).
  2. **Skill ליצירת אייקונים חדשים** בסגנון האחיד (SKILL.md/PROMPT.md/engine.js ל-Claude Code).

## רישיון - שלושה רישיונות נפרדים (LICENSING.md בריפו)
| חלק | רישיון | משמעות לנו |
|---|---|---|
| האייקונים (icons/, packages/, badges/) | **MIT** (LICENSE-ICONS) | ברשימת הרישיונות המאושרים של המשתמש. שימוש מסחרי, הפצה, שינוי - מותר. נוטיס זכויות יוצרים נשמר עם הקבצים. קרדיט לא חובה. |
| ה-Skill (SKILL.md, PROMPT.md, src/, scripts/) | Kubai Icons License (source-available, לא OSI) | שימוש חופשי כולל מסחרי; האייקונים שיוצרים איתו שייכים למשתמש בלי קרדיט. אסור להפיץ את ה-66 דוגמאות של src/icons.js כסט בפני עצמו. **אנחנו לא שולחים את ה-Skill בתיקייה** - לא נדרש. |
| האתר (site/, docs/) | All rights reserved | לא רלוונטי. |
- השמות Kubai/Lumno והלוגואים מחוץ לכל רישיון - לא משתמשים בשמות לצורך מיתוג.

## התאמה טכנית ל-HTML Content
- פורמט: SVG סטטי עצמאי. נבדק ישירות (grep על הקבצים שנשלחו): בלי `<script>`, בלי `href=`, בלי `src=`, בלי הפניות חוץ - רק `xmlns`. מתאים עקרונית למהדורת **Secure** (inline SVG מותר).
- id-ים פנימיים ממוספרים לפי שם אייקון (`loS-ki-chart-line` וכו') - אין התנגשות בין אייקונים שונים באותו עמוד. אותו אייקון פעמיים = id כפול (מרונדר תקין בדפדפנים, אפשר להוסיף סיומת).
- צלליות/הילה: פילטרים הצהרתיים של SVG (feGaussianBlur/feDropShadow). **לא נבדק ב-Power BI בפועל** - אם נחסמים, האייקון נראה שטוח אבל שלם. סומן בקובצי ההערות.
- גודל: 24-28px, viewBox עם שוליים לצל. אין תלות בפונטים.
- RTL: הסט שנבחר סימטרי/נייטרלי; אייקונים כיווניים (חצים) יידרשו שיקוף אופקי אם יתווספו.
- אבטחה: אין קוד, אין רשת - אין שטח תקיפה מעבר ל-SVG סטטי.

## מה נשלח בתיקייה
- `library/icons/` - 12 SVG נבחרים (banknote, hand-coins, coins, users, chart-line, chart-funnel, gauge, circle-alert, calendar, filter, target, clipboard-check) + LICENSE-MIT-kubai + README הטמעה.
- `examples/kpi-with-icon.dax` - כרטיס KPI מלא עם אייקון inline (מירכאות מוכפלות ל-DAX).
- הוכחת רינדור: כרטיסי KPI עם האייקונים ב-harness (נבדק בדפדפן בלבד, לא ב-Power BI).

## מסקנה
הכלי אומת, חינמי, והאייקונים תחת MIT - בתוך כללי הרישיון של המשתמש. אין צורך בהרשמה, תשלום או העלאת דאטה. ההטמעה בוצעה ברמת האייקונים הסטטיים (MIT), לא ברמת ה-Skill (source-available) - כך אין שום אילוץ רישיוני על התיקייה.
