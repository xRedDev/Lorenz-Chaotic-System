from manimlib import *
from scipy.integrate import solve_ivp

def lorenz_system(
        t, 
        state, 
        sigma: float = 10.0, 
        rho:   float = 28.0, 
        beta:  float = 8/3,
    ) -> list:
    
    '''
    Retorna una lista que contiene los sistemas evaluados en cada parámetro
    `x`, `y`, `z` en ODE's para determinar la tasa de cambio de las cantidades respecto al tiempo `t` tal como
    indica el original sistema de Ecuaciones de Lorenz.
    '''

    x, y, z = state # Archivar coordenadas en un solo estado
    dxdt = sigma * (y - x) # x es proporcional a la tasa de convección
    dydt = x * (rho - z) - y # y a la variación horizontal de la temperatura
    dzdt = x * y - beta * z # z a la variación vertical de la temperatura
    return [dxdt, dydt, dzdt] # lista con los sistemas


def ode_solution_points(
        function, 
        state0, 
        time: float,
        dt: float = 0.001,
    ):

    '''
    Retorna la solución al sistema `function` como puntos en un vector tridimensional (3D) por medio de `solve_ivp()` de scipy.integrate
    '''
    solution = solve_ivp(
        fun = function,
        t_span=(0, time),
        y0=state0,
        t_eval=np.arange(0, time, dt),
    )
    return solution.y.T # devolver la soluciones

class LorenzAttractor(Scene):
    '''
    Esta clase, `LorenzAttractor()` es la escena de contrucción para el Atractor de Lorenz
    '''
    def construct(self):
        # se crean los ejes donde se mostrarán las curvas de Lorenz
        axes = ThreeDAxes(
            x_range=(-50, 50, 5),
            y_range=(-50, 50, 5),
            z_range=(0, 50, 5),
            # personalizar tamaños
            width=16,
            height=16,
            depth=8,
        );

        axes.set_width(FRAME_WIDTH) # ocupar las dimensiones del canvas
        axes.center() # centrar
        
        self.frame.reorient(43, 76, 1, IN, 10) # orientar la cámara
        self.add(axes) # añadir los ejes al lienzo

        # Escuaciones de Lorenz en SVG-LaTeX para su posterior animación
        equations = Tex(
            R'''
            \begin{aligned}
            \frac{\mathrm{d} x}{\mathrm{~d} t} & =\sigma(y-x) \\
            \frac{\mathrm{d} y}{\mathrm{~d} t} & =x(\rho-z)-y \\
            \frac{\mathrm{d} z}{\mathrm{~d} t} & =xy-\beta z
            \end{aligned}
            ''', 
            # personalizar colores a cada simbolo de las ecuaciones de Lorenz
            t2c={
                "x": RED,
                "y": GREEN,
                "z": BLUE,
            },
            # tamaño de fuente menor al por defecto
            font_size=34, 
        );
        
        equations.fix_in_frame() # corregir en la pantalla, para que siempre aparezca en el marco del canvas
        equations.to_corner(UL)
        equations.set_z_index(2) # z index
        
        self.play(
            Write(equations)
        )
        self.wait()

        epsilon = 0.001 # \epsilon de variación
        evol_time = 30 # tiempo \t de evolución del sistema
        n_points = 6 # número de puntos a simular

        # generar dinámicamente una lista con todos los estados a simular y sus pequeñas variaciones \epsilon
        states: list = [
            [10, 10, 10 + n * epsilon] for n in range(n_points)
        ]

        # generar estados muy separados entre sí de forma aleatoria (segundo caso de sistema caótico)
        states_random = [
            [np.random.uniform(-30, 30), np.random.uniform(-30, 30), np.random.uniform(10, 40)]
            for _ in range(n_points)
        ]

        colors = color_gradient([BLUE_E, BLUE_A, YELLOW, TEAL, YELLOW_D, RED_A], len(states))

        curves = VGroup() # Inicializar un Objeto Matemático Vectorial que contendrá todos los estados ya calculados en función de `t`

        for state, color in zip(
            states, # usar `states_random` en lugar de `states` si se quiere simular estados iniciales muy diferentes entre sí
            colors): # Calcular cada evolución de los estados
            points = ode_solution_points(
                lorenz_system, 
                state,
                time=evol_time) # cálculo
            curve = VMobject().set_points_smoothly([axes.c2p(x, y, z) for x, y, z in points]) # gráfica
            curve.set_stroke(color=color, width=1) # color y stroke
            curves.add(curve) # añadir a la lista de curvas

        dots = Group(GlowDot(color=color, radius=0.5) for color in colors)

        globals().update(locals())

        # definir función actualizadora para los puntos animados (mover siempre al final de su curva)
        def update_dots(dots):
            for dot, curve in zip(dots, curves):
                dot.move_to(curve.get_end())

        dots.add_updater(update_dots) # añadir actualizador

        # generar dinámicamente un efecto de Trazado para cada punto (emplear si no se grafican las curvas)
        tail = VGroup(
            TracingTail(dot, time_traced=3).match_color(dot) # emparejar color del trazado con el de su respectivo punto
            for dot in dots
        );

        self.add(dots, tail)
       # curves.set_opacity(0)
        self.play(
            *(
                ShowCreation(curve, rate_func=linear)
                for curve in curves
            ),
            self.frame.animate.reorient(245, 72, 0, (0.0, 0.0, -1.0), 10.00),
            # Ir más lento
            run_time=evol_time * 1.5,
        )