import tkinter as tk


DAYS = ("월", "화", "수", "목", "금")
PERIODS = (
    "1교시 (09:00)",
    "2교시 (10:00)",
    "3교시 (11:00)",
    "4교시 (12:00)",
    "5교시 (13:00)",
    "6교시 (14:00)",
    "7교시 (15:00)",
    "8교시 (16:00)",
    "9교시 (17:00)",
)
RESULT_PROMPT = "공통 공강 찾기를 누르면 3명 모두 비어 있는 시간이 표시됩니다."
DEMO_SCHEDULES = (
    ((0, 0), (1, 0), (2, 0), (1, 1), (2, 1), (4, 2), (5, 2),
     (1, 3), (2, 3), (3, 3), (0, 4), (1, 4)),
    ((1, 0), (2, 0), (3, 0), (2, 1), (3, 1), (4, 1), (0, 2),
     (1, 2), (2, 3), (3, 3), (4, 3), (2, 4), (3, 4)),
    ((0, 0), (1, 0), (4, 0), (0, 1), (1, 1), (1, 2), (2, 2),
     (5, 2), (0, 3), (1, 3), (2, 3), (1, 4), (2, 4)),
)


class FreeTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("팀플 공통 공강 시간 추출기")
        self.root.minsize(760, 620)
        self.root.configure(bg="#f4f6f9")

        self.schedules = self._empty_schedules()
        self.current_member = 0
        self.result_mode = False
        self.cells = {}
        self.member_buttons = []

        self._build_ui()
        self._render_schedule()

    @staticmethod
    def _empty_schedules():
        return [
            [[False for _ in DAYS] for _ in PERIODS]
            for _ in range(3)
        ]

    def _build_ui(self):
        container = tk.Frame(self.root, bg="white", padx=22, pady=20)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="📅 팀플 공통 공강 시간 자동 추출기",
            font=("Malgun Gothic", 18, "bold"),
            bg="white",
            fg="#1e293b",
        ).pack(pady=(0, 6))
        tk.Label(
            container,
            text="팀원별 수업이 있는 교시를 클릭해 표시한 뒤, [공통 공강 찾기]를 누르세요.",
            font=("Malgun Gothic", 10),
            bg="white",
            fg="#64748b",
        ).pack(pady=(0, 16))

        controls = tk.Frame(container, bg="#f8fafc", padx=10, pady=10)
        controls.pack(fill="x", pady=(0, 14))

        tabs = tk.Frame(controls, bg="#f8fafc")
        tabs.pack(side="left")
        for index, name in enumerate(("팀원 1 (본인)", "팀원 2", "팀원 3")):
            button = tk.Button(
                tabs,
                text=name,
                command=lambda member=index: self.select_member(member),
                font=("Malgun Gothic", 9, "bold"),
                relief="flat",
                padx=10,
                pady=6,
                cursor="hand2",
            )
            button.pack(side="left", padx=(0, 5))
            self.member_buttons.append(button)

        actions = tk.Frame(controls, bg="#f8fafc")
        actions.pack(side="right")
        self._action_button(actions, "시연용 예제 입력", "#10b981", self.load_demo)
        self._action_button(actions, "전체 초기화", "#64748b", self.reset_all)
        self._action_button(actions, "공통 공강 찾기", "#f59e0b", self.find_common_free_time, "#1e293b")

        table = tk.Frame(container, bg="white")
        table.pack(fill="x")
        headers = ("교시 / 요일", *DAYS)
        for column, heading in enumerate(headers):
            tk.Label(
                table,
                text=heading,
                font=("Malgun Gothic", 9, "bold"),
                bg="#f1f5f9",
                fg="#1e293b",
                relief="solid",
                borderwidth=1,
                padx=6,
                pady=7,
            ).grid(row=0, column=column, sticky="nsew")
            table.grid_columnconfigure(column, weight=1)

        for period_index, period in enumerate(PERIODS):
            tk.Label(
                table,
                text=period,
                font=("Malgun Gothic", 9),
                bg="#f1f5f9",
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=6,
            ).grid(row=period_index + 1, column=0, sticky="nsew")
            for day_index in range(len(DAYS)):
                button = tk.Button(
                    table,
                    text="",
                    command=lambda p=period_index, d=day_index: self.toggle_slot(p, d),
                    font=("Malgun Gothic", 9),
                    relief="solid",
                    borderwidth=1,
                    padx=3,
                    pady=5,
                    cursor="hand2",
                    activebackground="#e2e8f0",
                )
                button.grid(row=period_index + 1, column=day_index + 1, sticky="nsew")
                self.cells[(period_index, day_index)] = button

        result = tk.LabelFrame(
            container,
            text="💡 추출된 공통 공강 시간",
            font=("Malgun Gothic", 10, "bold"),
            bg="#eff6ff",
            fg="#1e40af",
            padx=12,
            pady=10,
        )
        result.pack(fill="x", pady=(16, 0))
        self.result_label = tk.Label(
            result,
            text=RESULT_PROMPT,
            font=("Malgun Gothic", 10),
            bg="#eff6ff",
            fg="#1e293b",
            justify="left",
            anchor="w",
            wraplength=680,
        )
        self.result_label.pack(fill="x")

    @staticmethod
    def _action_button(parent, text, color, command, foreground="white"):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=foreground,
            activebackground=color,
            activeforeground=foreground,
            font=("Malgun Gothic", 9, "bold"),
            relief="flat",
            padx=9,
            pady=6,
            cursor="hand2",
        ).pack(side="left", padx=3)

    def select_member(self, member):
        self.current_member = member
        self.result_mode = False
        self._render_schedule()
        self._show_prompt()

    def toggle_slot(self, period, day):
        self.schedules[self.current_member][period][day] = not self.schedules[
            self.current_member
        ][period][day]
        self.result_mode = False
        self._render_schedule()
        self._show_prompt()

    def _render_schedule(self):
        for index, button in enumerate(self.member_buttons):
            selected = index == self.current_member
            button.configure(
                bg="#2563eb" if selected else "white",
                fg="white" if selected else "#1e293b",
                activebackground="#2563eb" if selected else "#e2e8f0",
            )

        for period in range(len(PERIODS)):
            for day in range(len(DAYS)):
                button = self.cells[(period, day)]
                if self.result_mode:
                    busy_count = sum(
                        schedule[period][day] for schedule in self.schedules
                    )
                    if busy_count == 0:
                        button.configure(
                            text="공통 공강",
                            bg="#bbf7d0",
                            fg="#166534",
                        )
                    else:
                        button.configure(
                            text=f"{busy_count}명 수업중",
                            bg="white",
                            fg="#333333",
                        )
                elif self.schedules[self.current_member][period][day]:
                    button.configure(text="수업", bg="#fecaca", fg="#991b1b")
                else:
                    button.configure(text="", bg="white", fg="#333333")

    def find_common_free_time(self):
        self.result_mode = True
        self._render_schedule()
        free_slots = [
            f"{DAYS[day]}요일 {period + 1}교시"
            for period in range(len(PERIODS))
            for day in range(len(DAYS))
            if not any(schedule[period][day] for schedule in self.schedules)
        ]

        if not free_slots:
            self.result_label.configure(
                text="3명 모두 겹치는 공강 시간이 없습니다. 점심시간이나 방과 후 시간을 활용하세요."
            )
            return

        self.result_label.configure(
            text=f"총 {len(free_slots)}개의 공통 빈 시간을 찾았습니다:\n"
            + "  ·  ".join(free_slots)
        )

    def load_demo(self):
        self.schedules = self._empty_schedules()
        for member, slots in enumerate(DEMO_SCHEDULES):
            for period, day in slots:
                self.schedules[member][period][day] = True
        self.current_member = 0
        self.result_mode = False
        self._render_schedule()
        self._show_prompt()

    def reset_all(self):
        self.schedules = self._empty_schedules()
        self.current_member = 0
        self.result_mode = False
        self._render_schedule()
        self._show_prompt()

    def _show_prompt(self):
        self.result_label.configure(text=RESULT_PROMPT)


def main():
    root = tk.Tk()
    FreeTimeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
