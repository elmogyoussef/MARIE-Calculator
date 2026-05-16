#include <stdio.h>
int AC  = 0;
int MAR = 0;
int MBR = 0;

#define MEM_OPERAND  5
#define MEM_TEMP     6
int memory[16];

void exec_input(int value) {
    printf("  [EXECUTE  INPUT]\n");
    AC = value;
    printf("    AC  <- input        AC  = %d\n", AC);
}
void exec_store(int addr) {
    printf("  [EXECUTE  STORE %d]\n", addr);
    MAR = addr;
    printf("    MAR <- %d            MAR = %d\n", addr, MAR);
    MBR = AC;
    printf("    MBR <- AC           MBR = %d\n", MBR);
    memory[MAR] = MBR;
    printf("    M[MAR] <- MBR       M[%d] = %d\n", MAR, memory[MAR]);
}
void exec_load(int addr) {
    printf("  [EXECUTE  LOAD %d]\n", addr);
    MAR = addr;
    printf("    MAR <- %d            MAR = %d\n", addr, MAR);
    MBR = memory[MAR];
    printf("    MBR <- M[MAR]       MBR = %d\n", MBR);
    AC = MBR;
    printf("    AC  <- MBR          AC  = %d\n", AC);
}
void exec_add(int addr) {
    int old_AC;
    printf("  [EXECUTE  ADD %d]\n", addr);
    MAR = addr;
    printf("    MAR <- %d            MAR = %d\n", addr, MAR);
    MBR = memory[MAR];
    printf("    MBR <- M[MAR]       MBR = %d\n", MBR);
    old_AC = AC;
    AC = AC + MBR;
    printf("    AC  <- AC + MBR     %d + %d = %d\n", old_AC, MBR, AC);
}
void exec_subt(int addr) {
    int old_AC;
    printf("  [EXECUTE  SUBT %d]\n", addr);
    MAR = addr;
    printf("    MAR <- %d            MAR = %d\n", addr, MAR);
    MBR = memory[MAR];
    printf("    MBR <- M[MAR]       MBR = %d\n", MBR);
    old_AC = AC;
    AC = AC - MBR;
    printf("    AC  <- AC - MBR     %d - %d = %d\n", old_AC, MBR, AC);
}
void exec_clear(void) {
    printf("  [EXECUTE  CLEAR]\n");
    AC = 0;
    printf("    AC  <- 0            AC  = %d\n", AC);
}
void exec_halt(void) {
    printf("  [EXECUTE  HALT]\n");
    printf("    Processor HALTED.\n");
}
void do_add(int x) {
    printf("  Operation: ADD %d\n", x);
    exec_store(MEM_TEMP);
    exec_input(x);
    exec_store(MEM_OPERAND);
    exec_load(MEM_TEMP);
    exec_add(MEM_OPERAND);
}
void do_subt(int x) {
    printf("  Operation: SUBT %d\n", x);
    exec_store(MEM_TEMP);
    exec_input(x);
    exec_store(MEM_OPERAND);
    exec_load(MEM_TEMP);
    exec_subt(MEM_OPERAND);
}
void do_clear(void) {
    printf("  Operation: CLEAR\n");
    exec_clear();
}
void do_halt(void) {
    printf("  Operation: HALT\n");
    exec_halt();
}
void marie_set_AC(int value) {
    do_clear();
    do_add(value);
}
int marie_sum(int data[], int count) {
    int i;
    do_clear();
    for (i = 0; i < count; i++) {
        do_add(data[i]);
    }
    return AC;
}
int marie_average(int data[], int count) {
    int avg;
    if (count == 0) {
        do_clear();
        return AC;
    }
    marie_sum(data, count);     
    avg = AC / count;            
    marie_set_AC(avg);           
    return AC;
}
int marie_max(int data[], int count) {
    int i;
    int max_val;

    if (count <= 0) {
        do_clear();
        return AC;
    }

    marie_set_AC(data[0]);
    max_val = data[0];

    for (i = 1; i < count; i++) {

        exec_store(MEM_TEMP);
        exec_input(data[i]);
        exec_store(MEM_OPERAND);

        exec_load(MEM_TEMP);
        exec_subt(MEM_OPERAND);   

        if (AC < 0) {
        
            max_val = data[i];
        }

        marie_set_AC(max_val);
    }

    return AC;
}
void marie_sort(int data[], int count) {
    int i, j, temp_val;

    if (count <= 1) {
        if (count == 1)
            marie_set_AC(data[0]);
        else
            do_clear();
        return;
    }

    for (i = 0; i < count - 1; i++) {
        for (j = 0; j < count - 1 - i; j++) {

            marie_set_AC(data[j]);
            exec_store(MEM_TEMP);

            exec_input(data[j + 1]);
            exec_store(MEM_OPERAND);

            
            exec_load(MEM_TEMP);
            exec_subt(MEM_OPERAND);   

            if (AC > 0) {             
                temp_val   = data[j];
                data[j]    = data[j + 1];
                data[j + 1] = temp_val;
            }
        }
    }


    marie_set_AC(data[0]);
}

void read_data(int data[], int *count) {
    int i;
    printf("  Number of values: ");
    scanf("%d", count);
    if (*count < 1) {
        *count = 0;
        return;
    }
    for (i = 0; i < *count; i++) {
        printf("  Enter value %d: ", i + 1);
        scanf("%d", &data[i]);
    }
}

int main(void) {
    int choice, x;
    int values[100];
    int count;
    int result;
    int i;

    printf("  ================================================\n");
    printf("           MARIE Calculator Simulator\n");
    printf("  ================================================\n");
    printf("  AC starts at 0. Each operation shows\n");
    printf("  the full register-transfer trace.\n");
    printf("  ================================================\n\n");

    while (1) {
        printf("  Current  AC = %d\n", AC);
        printf("  +----------------------+\n");
        printf("  | 1. ADD               |\n");
        printf("  | 2. SUBT              |\n");
        printf("  | 3. CLEAR             |\n");
        printf("  | 4. SUM               |\n");
        printf("  | 5. AVERAGE           |\n");
        printf("  | 6. MAX               |\n");
        printf("  | 7. SORT              |\n");
        printf("  | 8. EXIT              |\n");
        printf("  +----------------------+\n");
        printf("  Choice: ");
        scanf("%d", &choice);

        if (choice == 1 || choice == 2) {
            printf("  Enter number: ");
            scanf("%d", &x);
        }

        switch (choice) {
            case 1:
                do_add(x);
                break;
            case 2:
                do_subt(x);
                break;
            case 3:
                do_clear();
                break;
            case 4:
                read_data(values, &count);
                if (count > 0) {
                    result = marie_sum(values, count);
                    printf("  Sum = %d\n", result);
                } else {
                    printf("  No values to sum.\n");
                }
                break;
            case 5:
                read_data(values, &count);
                if (count > 0) {
                    result = marie_average(values, count);
                    printf("  Average = %d\n", result);
                } else {
                    printf("  No values to average.\n");
                }
                break;
            case 6:
                read_data(values, &count);
                if (count > 0) {
                    result = marie_max(values, count);
                    printf("  Max = %d\n", result);
                } else {
                    printf("  No values to find max.\n");
                }
                break;
            case 7:
                read_data(values, &count);
                if (count > 0) {
                    marie_sort(values, count);
                    printf("  Sorted: ");
                    for (i = 0; i < count; i++)
                        printf("%d ", values[i]);
                    printf("\n");
                } else {
                    printf("  No values to sort.\n");
                }
                break;
            case 8:
                do_halt();
                return 0;
            default:
                printf("  Invalid choice.\n\n");
                break;
        }

        printf("\n");
    }

    return 0;
}