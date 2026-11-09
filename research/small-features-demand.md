# מחקר תוספת: פיצ׳רים קטנים ותסכולים יומיומיים (נשלף חי 09/11/2026)

בקשת המשתמש (10:18): "תבדוק עוד דברים אפילו אם זה פיצ׳רים קטנים.. מחקר עוד יותר מעמיק".
שיטה: איתור שרשורי תסכול/בקשות, שליפת התוכן המלא, חילוץ בקשות קונקרטיות עם ציטוט, תאריך וקוביית קהל (נקודות), ובדיקת סטטוס: מה הסטטוס הנטיבי (אם אומת מול תיעוד Microsoft - מצוין; אחרת "לפי דיווחי משתמשים, לא אומת במסמכים"), והאם HTML Content פותר (Secure סטטי / Regular JS / לא).

## מקורות (URLs מדויקים שנשלפו)
- S1: https://www.reddit.com/r/PowerBI/comments/1fzxi0c/whats_annoying_about_powerbi/ (שרשור 09/10/2024, 45 נק׳, 187 תגובות)
- S2: https://www.reddit.com/r/PowerBI/comments/1kl0dy0/what_frustrates_you_about_power_bi/ (12/05/2025, 135 נק׳, 151 תגובות)
- S3: https://www.reddit.com/r/PowerBI/comments/1k0moxt/what_is_a_brand_new_functionality_you_want_to_see/ (16/04/2025, 54 נק׳, 189 תגובות)
- S4: https://spilledgraphics.com/powerbi/011-my-power-bi-wishlist/ (בלוג, 6 משאלות מפורטות עם דוגמאות מה-Economist/Washington Post)
- S5: https://community.fabric.microsoft.com/idea/fbc_ideas/enable-text-style-formatting-inside-dax-for-more-power/4884694 (Fabric Ideas, פורסם ~11 חודשים לפני הבדיקה)

## א. פערים שהספרייה הקיימת עונה עליהם (עם ראיות)

| # | בקשה (ציטוט, מקור, תאריך, נק׳) | סטטוס נטיבי | פתרון בספרייה |
|---|---|---|---|
| 1 | "A MATRIX VISUAL THAT DOESN'T SUCK" (S3, anxiouscrimp, 16/04/2025, 105 נק׳); "The matrix visual SUCKS. It should have the same formatting options as a pivot table on excel" (S1, Accomplished-Fee6953, 10/10/2024); "The matrix visual" (S2, pvnptl123, 46 נק׳) | **אומת מול המסמך הבעלים** (https://learn.microsoft.com/en-us/power-bi/visuals/desktop-matrix-visual, 09/11/2026): המטריקס שופר משמעותית - רוחב עמודה פר-עמודה בפיקסלים, רוחב מותנה (fx), custom totals, freeze headers. התלונה על רוחב עמודות (79 נק׳ ב-2024) **טופלה נטיבית**. מה שעדיין אין: חופש עיצוב מלא ברמת תא בודד (CSS שרירותי) | `data-table` / `scorecard-table` - הערך שנשאר: שליטת CSS מלאה, ספארקליינים בתא, אייקונים |
| 2 | "pie charts where it cuts off the words on the legend instead of wrapping them" (S1, Problemilyyy, 09/10/2024, 15 נק׳) | לפי דיווח | `donut-legend` - מקרא HTML עם גלישת שורות |
| 2b | ראו #2: אומת מול המסמך הבעלים (https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-customize-title-background-and-legend, 09/11/2026): הגדרות המקרא = הדלקה/כיבוי, כותרת, מיקום, צבע, פונט - **אין text wrap לפריטי מקרא**. התלונה בתוקף |
| 3 | "the data labels in a chart cannot be moved like in Excel" (S2, Salt_Bug4223, 12/05/2025, 15 נק׳) | לפי דיווח | תוויות HTML במיקום חופשי בכל הרכיבים (ראו milestone-timeline: 6 תוויות ללא חפיפה ב-360px) |
| 4 | "make a column header or certain cells bold - 2 clicks in excel but 3 hours of trial and error in PBI" (S2, Prestigious-Deer-103, 12/05/2025, 10 נק׳) | לפי דיווח | `data-table` - CSS חופשי על כל תא |
| 5 | "we cannot do conditional formatting on a series in a bar chart (happens weekly)" (S2, casperseve, 13/05/2025, 8 נק׳) | לפי דיווח | `condition-bar` / `progress-bar` - צבע מותנה ב-DAX |
| 6 | "Cards are very limited" (S2, crasspy, 12/05/2025) | לפי דיווח | כל שורת ה-KPI + אייקוני Kubai (חדש) |
| 7 | "Slicers can't be vertical... And those big bubbles on slicers are driving me mad" (S1, Cornokz, 09/10/2024, 4 נק׳) | לפי דיווח | `slicer-chips` (תצוגה בלבד, לא שליטה בסלייסרים אחרים) |
| 8 | "Ability to specify Custom CSS for every element - for each table column separately, row/column headers, titles, subtitles" (S3, Ok-Boysenberry3950, 16/04/2025, 14 נק׳) | בקשת פיצ׳ר פתוחה | זו בדיוק מהות HTML Content - CSS על כל אלמנט |
| 9 | "conditional formatting affects the whole cell... you cannot highlight or emphasize separate parts of the text" (S5, Fabric Idea) | רשמי: הצעה פתוחה ב-Fabric Ideas. **חשוב:** התגובה המובילה בעמוד (Joe_Barry, ~11 חודשים) קובעת: "It is possible at the moment using HTML. You can use the HTML Content visual by Daniel Marsh-Patrick" | פטרן spans מעוצבים בתוך מחרוזת אחת - קיים ברכיבי ה-KPI |

## ב. פערים שהספרייה עוד לא עונה עליהם - אפשרי ב-HTML Content (Secure סטטי)

| # | בקשה (ציטוט, מקור, תאריך, נק׳) | סטטוס נטיבי | יישום מוצע |
|---|---|---|---|
| 10 | "Histograms." (S3, ThomasMarkov, 16/04/2025, 19 נק׳); "Lack of histograms+box and whisker plots in core visuals" (S1, GossipGirlX0X0, 09/10/2024, 5 נק׳) | **אומת מול קטלוג הסוגים הרשמי** (https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a, 09/11/2026): אין סוג histogram (יש column/bar/ribbon/waterfall/funnel/Gantt-preview וכו'). workaround נטיבי: binning ידני + column chart. HTML: bins ב-DAX + עמודות SVG עם תוויות bins נקיות |
| 11 | "Native pareto chart." (S3, CaptCurmudgeon, 16/04/2025, 10 נק׳) | לפי דיווח | עמודות ממוינות + קו מצטבר %, אותו פטרן של bullet-with-trend |
| 12 | box plot (S1, כנ״ל, 5 נק׳) | לפי דיווח | חמישיה חמישנית ב-DAX + ציור SVG סטטי |
| 13 | "No easy way to do topN and 'others'" (S1, Dapperscavenger, 09/10/2024, 4 נק׳) | לפי דיווח | לא רכיב - תבנית DAX (GROUP BY + שורת Others). אפשר להוסיף כדף פטרן |
| 14 | "just ask for a full Font list rather than what microsoft decide i can have" (S3, Photog_72, 16/04/2025, 24 נק׳) | אומת חלקית (https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes, 09/11/2026): theme JSON נותן שליטה בפונטים, אבל הרינדור מוגבל לפונטים הזמינים ב-Power BI - אין העלאת פונט שרירותי. HTML Content: Secure = פונטי מערכת; Regular עם web fonts: לא אומת - לא לטעון |

## ג. פערים ש-HTML Content לא יפתור (חשוב ליישור ציפיות)

| # | בקשה (ציטוט, מקור, תאריך, נק׳) | למה לא |
|---|---|---|
| 15 | "No write back option / commenting" (S1, gaius_julius_caegull, 09/10/2024, 14 נק׳) | HTML Content לא כותב למודל |
| 16 | "I want a button: export to excel" (S2, Lauren-Ipsum-128, 12/05/2025, 10 נק׳) | ויז׳ואל לא יכול להפעיל ייצוא |
| 17 | כל 6 משאלות S4: cross-highlighting בין small multiples, tooltips מסונכרנים עם קו אנכי משותף, brushing | תיקון דיוק (אומת מול התיעוד הרשמי https://html-content.com/docs/interactivity, 09/11/2026): **סינון-צולב בלחיצה כן נתמך** - דרך Context data role, Power BI מיישב את האלמנט לשורת דאטה ומסנן ויז׳ואלים אחרים (עובד גם ב-Secure, בלי script; יש גם tooltips, drillthrough ו-context menu). מה שלא אפשרי: סנכרון חי ברמת JS בין שני ויז׳ואלים (hover בוויז׳ואל אחד שמאיר נקודה באחר) - אין ערוץ תקשורת כזה. כלומר: click-to-filter משותף = כן; hover-sync חי = לא |
| 18 | "Slicer Default values" / "A slicer that picks the latest date" (S3, chubs66 58 נק׳, konwiddak 7 נק׳) | HTML Content לא שולט במצב סלייסרים אחרים. **נטיבי חלקי** (אומת מול https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers, 09/11/2026): סלייסר תאריך יחסי ("last full month") מתגלגל אוטומטית בכל טעינה - מכסה את מקרה "התאריך האחרון" לתאריכים בלבד; default לערכים שאינם תאריך עדיין פתוח |
| 19 | "page level security" (S2, yyavuz, 122 נק׳; S3, attaboy000, 80 נק׳) | ברמת השירות, לא ויז׳ואל |

## סדר עדיפויות מוצע (מבוסס ניקוד קהל + הלימה לספרייה)
1. שולחן/מטריקס (#1) - הבקשה החזקה ביותר במדגם; מכוסה - לוודא שהדוגמאות מדגישות זאת.
2. Histogram (#10) - הבקשה החזקה הבאה שלא מכוסה; ישים.
3. Pareto (#11), box plot (#12) - ישימים, ניקוד בינוני.
4. TopN+Others (#13) - דף פטרן DAX זול.
5. לא להבטיח: writeback, export, סנכרון בין-וויז׳ואלי, שליטה בסלייסרים (ג׳).


## החלטה מהותית (09/11/2026, אחרי אימות המסמכים)
**מוסיפים: histogram** - הבקשה הלא-מכוסה החזקה ביותר (19+5 נק׳ בשני שרשורים), אין סוג נטיבי (אומת בקטלוג הרשמי), ישים כ-SVG סטטי ב-Secure, וערך HTML אמיתי: תוויות bins קריאות, צבע מותנה, גבולות מדויקים - בלי workaround של binning ידני.
בהמתנה מתועדת: pareto (10 נק׳), box plot (5 נק׳), TopN+Others (דף פטרן DAX).
תיקון חשוב למסר למשתמש: HTML Content כן תומך בסינון-צולב בלחיצה (Context role) - אין לומר "אין אינטראקטיביות בין ויז׳ואלים" בלי ההבחנה הזו.
