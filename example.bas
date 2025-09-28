10 REM *** Пример ByteBasic: все базовые конструкции ***
16 REM
17 REM
20 PRINT "Привет! Введи число от 1 до 10:"
30 INPUT N
40 IF N < 1 THEN GOTO 20
50 IF N > 10 THEN GOTO 20

60 REM Считаем факториал с помощью цикла FOR
70 LET FACT = 1
80 FOR I = 1 TO N
90 LET FACT = FACT * I
100 NEXT I

110 PRINT "Факториал "; N; " равен "; FACT

120 REM Используем GOSUB для вычисления суммы чисел от 1 до N
130 LET SUM = 0
140 LET I = 1
150 GOSUB 200
160 PRINT "Сумма чисел от 1 до "; N; " равна "; SUM

170 REM DATA и READ
180 DATA 3, 5, 7, 9
190 READ A, B, C, D
195 PRINT "Данные из DATA: "; A; B; C; D

200 REM Подпрограмма для суммы от I до N
210 IF I > N THEN RETURN
220 LET SUM = SUM + I
230 LET I = I + 1
240 GOTO 210

250 REM Завершение
260 PRINT "Спасибо за использование ByteBasic!"
270 END
