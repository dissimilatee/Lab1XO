# -*- coding: utf-8 -*-
import csv
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

REPO = "https://github.com/dissimilatee/Lab1XO"   # <- вставити посилання
d = Document()
st = d.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(13)
for s in d.sections: s.left_margin = Cm(3); s.right_margin = Cm(1.5)

def c(t, bold=False, size=None):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(t); r.bold = bold
    if size: r.font.size = Pt(size)
def h(t): d.add_heading(t, level=1)
def p(t): d.add_paragraph(t)
def code(t):
    q = d.add_paragraph(); r = q.add_run(t); r.font.name = 'Courier New'; r.font.size = Pt(9)
def img(path, w=15, cap=None):
    d.add_picture(path, width=Cm(w)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cap: c(cap, size=11)

c("Київський національний університет імені Тараса Шевченка", True)
c("Факультет комп’ютерних наук та кібернетики", True)
for _ in range(3): d.add_paragraph()
c("ЗВІТ", True, 18)
c("з лабораторної роботи № 1 з дисципліни «Хмарні обчислення»")
c("Тема 8.4: паралельне обчислення біноміальних коефіцієнтів, комбінацій і перестановок на платформі PARCS-Python у Google Cloud Platform", True)
for _ in range(3): d.add_paragraph()
c("Виконав: студент групи ТТП-42 Бондаренко Максим")
c("Київ — 2026")
d.add_page_break()

h("Мета роботи")
p("Реалізувати паралельне обчислення C(n,k) і P(n,k) із застосуванням системи PARCS-Python, розгорнути кластер (master і чотири worker) у Google Cloud Platform, порівняти час послідовної та паралельної версій для 1, 2, 3 і 4 воркерів.")

h("1. Ідея алгоритму")
p("Кількість перестановок P(n,k) = n!/(n−k)! = ∏(n−k+i), i = 1..k, а число комбінацій C(n,k) = P(n,k)/k!, де k! = ∏ i. Усе зводиться до добутку чисел на діапазоні 1..k.")
p("Master ділить діапазон 1..k на N відрізків, довжини яких відрізняються щонайбільше на 1 (map). Кожен воркер незалежно рахує добуток (n−k+i) і добуток i на своєму відрізку. Master перемножує часткові добутки (reduce) і знаходить C(n,k) = P(n,k)·(k!)⁻¹. Воркери не обмінюються даними між собою.")
p("Для вимірювань використано режим mod (обчислення за модулем простого числа 1 000 000 007, потрібно n < модуль, ділення через обернений елемент). Вхід: n = 300 000 000, k = 150 000 000. Воркеру передається кілька чисел, а повертається пара чисел: обсяг мережевого обміну не залежить від розміру задачі, тому накладні витрати малі. Є також режим exact (точні великі числа, hex-рядки по мережі), але там master виконує послідовне множення й ділення великих чисел, і масштабування гірше, тому для замірів його не використано.")

h("2. Помилки збірки та налаштування, пов’язані із застарілими версіями")
p("1) Команда gcloud compute instances create-with-container, наведена в README parcs-python, більше не працює: Google припинила підтримку контейнерного агента. Замість неї створюються звичайні VM з Ubuntu 22.04, а startup-скрипт (cloud/startup.sh) встановлює Docker і запускає образ hummer12007/parcs-node з --network host. Роль (master або worker і IP master) передається в метаданих VM.")
p("2) PARCS-Python працює на Python 2.7. У ньому range() створює список у пам’яті: на діапазоні 150 млн елементів процес воркера завершувався з «Killed» (нестача пам’яті). Виправлення: на початку модуля try: range = xrange / except NameError: pass. Код також залишається сумісним з Python 3.")
p("3) Помилка в одній задачі зупиняє потік-планувальник master (виняток у destroy_workers), і нові задачі залишаються у стані Not Started. Лікування: перезапустити контейнер parcs на master (docker restart parcs), а потім на воркерах, щоб вони заново зареєструвались.")
p("4) У зоні europe-north1-a виник stockout (немає вільних ресурсів); використано європейську зону europe-west4-a і тип e2-medium.")
p("5) Із нового мережевого оточення порт 8080 master був недоступний напряму, тому веб-інтерфейс PARCS відкривався через SSH-тунель (gcloud compute ssh master -- -N -L 8081:localhost:8080).")

h("3. Налаштування хмарного сервісу (команди)")
code("""# gcloud auth login; створити проєкт, підключити білінг, увімкнути API
gcloud projects create <PROJECT>
gcloud config set project <PROJECT>
gcloud billing projects link <PROJECT> --billing-account=<BILLING_ID>
gcloud services enable compute.googleapis.com
gcloud config set compute/zone europe-west4-a

# firewall: трафік усередині мережі + веб-інтерфейс лише з вашої IP
gcloud compute firewall-rules create parcs-internal --network=default --direction=INGRESS --action=ALLOW --rules=all --source-ranges=10.0.0.0/8
gcloud compute firewall-rules create parcs-web --network=default --direction=INGRESS --action=ALLOW --rules=tcp:8080,tcp:22 --source-ranges=<ВАША_IP>/32

# master
gcloud compute instances create master --machine-type=e2-medium --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --metadata=parcs-args=master --metadata-from-file=startup-script=cloud/startup.sh
# worker1..worker4 (IP master — внутрішня)
gcloud compute instances create worker1 worker2 worker3 worker4 --machine-type=e2-medium --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --metadata="parcs-args=worker <MASTER_INTERNAL_IP>" --metadata-from-file=startup-script=cloud/startup.sh

# запуск замірів (3 повтори для N = 1..4)
./cloud/run_all.sh <MASTER_IP:8080> 3
# після замірів — видалити VM
gcloud compute instances delete master worker1 worker2 worker3 worker4""")
p("Веб-інтерфейс PARCS: http://<MASTER_IP>:8080 (Add Job: solution.py та input.txt). Доступ відкрито лише з IP автора.")

h("4. Кластер і виконання")
img("report/img/1_vms.png", 15, "Рис. 1. Віртуальні машини: master і worker1–worker4")
img("report/img/2_nodes.png", 12, "Рис. 2. Воркери, зареєстровані в PARCS (вкладка Nodes)")
img("report/img/3_jobs.png", 12, "Рис. 3. Запуски для N = 1, 2, 3, 4 воркерів (вкладка Jobs)")

h("5. Результати")
p("Час виконання виміряно всередині задачі (solve), медіана з трьох прогонів. Послідовний еталон — sequential.py під Python 2 на тій самій конфігурації VM (медіана трьох). Усі прогони дали C(n,k) mod 1e9+7 = 940400276 і P(n,k) mod 1e9+7 = 591392064, що збігається з послідовною версією й з math.comb/math.perm на малих вхідних даних.")
rows = list(csv.DictReader(open('results.csv')))
t1 = [float(r['time_s']) for r in rows if r['workers'] == '1'][0]
tb = d.add_table(rows=1, cols=3); tb.style = 'Table Grid'
for i, t in enumerate(["Воркерів", "Час, с", "Прискорення (відносно 1 воркера)"]): tb.rows[0].cells[i].text = t
for r in rows:
    w, t = int(r['workers']), float(r['time_s'])
    cells = tb.add_row().cells
    cells[0].text = "послідовна" if w == 0 else str(w)
    cells[1].text = "%.2f" % t
    cells[2].text = "—" if w == 0 else "%.2f×" % (t1 / t)
d.add_paragraph()
img("report/img/4_plot.png", 16, "Рис. 4. Залежність часу виконання й прискорення від кількості воркерів")
p("Час майже обернено пропорційний кількості воркерів: прискорення 2,00× для двох, 2,96× для трьох і 3,91× для чотирьох воркерів, що близько до ідеального. Невеликий відрив від ідеалу пояснюється фіксованими витратами на запуск задачі та розсилку. Час з одним воркером (24,75 с) трохи менший за послідовний (26,87 с), але в межах розкиду замірів на спільній VM (послідовні прогони дали 26,4–36,2 с).")

h("Висновки")
p("Задача біноміальних коефіцієнтів добре розпаралелюється на PARCS: обчислень багато, а даних для передачі мало, тому майже лінійне прискорення зберігається до чотирьох воркерів. Основні труднощі були пов’язані із застарілістю платформи: Python 2 і непрацюючий спосіб розгортання контейнерів у GCP.")

h("Посилання на GitHub")
p(REPO)
d.core_properties.author = 'Бондаренко Максим'
d.core_properties.last_modified_by = 'Бондаренко Максим'
d.core_properties.title = 'Звіт з лабораторної роботи №1'
d.save('report/Звіт_ЛР1_Бондаренко.docx')
