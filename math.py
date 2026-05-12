# Copyright 2026 Marimo. All rights reserved.

import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    # imports and graphical representation of derivatives
    import marimo as mo
    import sympy as sm
    from sympy import Matrix, sin, cos, tan, sqrt, simplify, collect
    from sympy.physics.mechanics import (
        vlatex,
        ReferenceFrame,
        Point,
        Particle,
        dynamicsymbols,
        kinetic_energy,
    )
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
    )
    from types import SimpleNamespace


    def _vlatex_mime(self):
        return ("text/html", mo.md(f"$${vlatex(self)}$$").text)

    sm.Matrix._mime_ = _vlatex_mime
    sm.Basic._mime_ = _vlatex_mime
    sm.physics.mechanics._mime_ = _vlatex_mime
    sm.physics.mechanics.Vector._mime_ = _vlatex_mime

    N = ReferenceFrame("N")
    O = Point("O")
    O.set_vel(N, 0)
    t = sm.Symbol('t')
    get_memoria, set_memoria = mo.state({})
    mo.outline(label="Table of Contents")
    return (
        Matrix,
        N,
        O,
        Particle,
        Point,
        SimpleNamespace,
        dynamicsymbols,
        get_memoria,
        implicit_multiplication_application,
        mo,
        parse_expr,
        set_memoria,
        simplify,
        sm,
        standard_transformations,
        t,
        vlatex,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lagrangian coordinates
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # --- CELLA 2: DEFINIZIONE SIMBOLI GLOBALI ---
    mo.md("## 1. Definizione dell'Universo Simbolico")

    parametri_input = mo.ui.text(
        label="Parametri fisici (es: m, M, L, g)", 
        placeholder="m, l, g, omega, k",
        value="m, l, g, omega, k"
    )

    coordinate_input = mo.ui.text(
        label="Coordinate Lagrangiane (es: theta, x)", 
        placeholder="x, theta",
        value="x, theta"
    )

    mo.vstack([parametri_input, coordinate_input])
    return coordinate_input, parametri_input


@app.cell(hide_code=True)
def _(
    Matrix,
    SimpleNamespace,
    coordinate_input,
    dynamicsymbols,
    mo,
    parametri_input,
    sm,
    vlatex,
):
    # --- CELLA 3: LOGICA DI PARSING DEI SIMBOLI ---
    # Creiamo il dizionario locale per il parser
    nomi_parametri = [
        s.strip() for s in parametri_input.value.split(",") if s.strip()
    ]
    nomi_coordinate = [
        s.strip() for s in coordinate_input.value.split(",") if s.strip()
    ]

    simboli_fisici = {s: sm.Symbol(s, real=True, positive=True) for s in nomi_parametri}
    simboli_lagrange = {s: dynamicsymbols(s) for s in nomi_coordinate}
    q = Matrix([x for x in simboli_lagrange.values()])
    qd = Matrix([dynamicsymbols(x, 1) for x in simboli_lagrange.keys()])

    # Uniamo tutto in un dizionario per sympy.parse_expr
    # Includiamo anche funzioni standard come sin, cos, ecc.
    dict_simboli = {
        **simboli_fisici,
        **simboli_lagrange,
        "sin": sm.sin,
        "cos": sm.cos,
        "tan": sm.tan,
        "pi": sm.pi,
    }

    # Uniamo i dizionari e li convertiamo in un oggetto
    s = SimpleNamespace(**dict_simboli)

    mo.vstack(
        (
            mo.md(
                rf"""**Physical quantities:** 
                \[{r'\quad '.join([vlatex(x) for x in simboli_fisici.values()])}\]"""
            ),
            mo.md(rf"""**Lagrangian coordinates and derivatives**
    $$q = {vlatex(q)} \qquad \dot q = {vlatex(qd)}$$
    """),
        )
    )
    return dict_simboli, q, qd, s


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Points and kinematics
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # --- CELLA 4: SELETTORE NUMERO PARTICELLE ---
    mo.md("## 2. Configurazione del Sistema")

    n_particelle = mo.ui.number(start=1, stop=10, step=1, value=1, label="Numero di particelle")
    n_particelle
    return (n_particelle,)


@app.cell(hide_code=True)
def _(get_memoria, mo, n_particelle, set_memoria):
    number = mo.ui.number(start=1, stop=n_particelle.value, label="Inspect Point")
    memoria = get_memoria()


    def ottieni_default(idx, chiave, fallback):
        """Recupera il valore dalla memoria se esiste, altrimenti usa il fallback."""
        return str(memoria.get(f"{chiave}_{idx}", fallback))


    def salva_stato(dati_form):
        set_memoria(memoria | dict(dati_form.items()))


    # 1. Costruiamo dinamicamente l'intestazione e le righe di una tabella Markdown
    md_point_table = (
        "| Point | Mass | X | Y | Z |\n|:---:|:---:|:---:|:---:|:---:|\n"
    )
    for jp in range(1, n_particelle.value + 1):
        md_point_table += f"""| **{jp}** | {{mass_{jp}}} | {{X_{jp}}} | {{Y_{jp}}} |{{Z_{jp}}} |\n"""

    point_table = {}
    for jp in range(1, 1 + n_particelle.value):
        point_table[f"mass_{jp}"] = mo.ui.text(
            # label="mass",
            value=ottieni_default(jp, "mass", "m"),
            placeholder="m",
        )
        point_table[f"X_{jp}"] = mo.ui.text(
            label=" ",
            value=ottieni_default(jp, "X", "x+l*sin(theta)"),
            placeholder="pos x",
        )
        point_table[f"Y_{jp}"] = mo.ui.text(
            label=" ",
            value=ottieni_default(jp, "Y", "-l*cos(theta)"),
            placeholder="pos y",
        )
        point_table[f"Z_{jp}"] = mo.ui.text(
            label=" ",
            value=ottieni_default(jp, "Z", "0"),
            placeholder="pos z",
        )
    # 3. Generiamo l'elemento UI unificato
    # .batch() prende i widget e li inietta nel layout, rendendo il tutto un unico blocco reattivo
    point_table = (
        mo.md(md_point_table)
        .batch(**point_table)
        .form(
            show_clear_button=True,
            bordered=True,
            on_change=salva_stato,
        )
    )
    # Visualizzazione (sarà una classica tabella HTML pulita)
    mo.vstack(
        [
            mo.md("""## Points 
            if you need just a geometric point (like a fix anchor for a spring)
            remember to set the mass to 0"""),
            point_table,
        ]
    )
    return (point_table,)


@app.cell(hide_code=True)
def _(
    N,
    O,
    Particle,
    Point,
    dict_simboli,
    implicit_multiplication_application,
    n_particelle,
    parse_expr,
    point_table,
    standard_transformations,
):
    transformations = standard_transformations + (
        implicit_multiplication_application,
    )
    punti = []
    particelle = []
    if point_table.value is not None:
        for i in range(1, n_particelle.value+1):
            values = [point_table.value[f"mass_{i}"], 
                     point_table.value[f"X_{i}"], 
                     point_table.value[f"Y_{i}"], 
                     point_table.value[f"Z_{i}"], ]
            mass, X, Y, Z = [
                parse_expr(
                    str_input, local_dict=dict_simboli, transformations=transformations
                )
                for str_input in values
            ]
            P_i = Point(f"P{i}")

            P_i.set_pos(O, X * N.x + Y * N.y + Z * N.z)
            P_i.set_vel(N, P_i.pos_from(O).dt(N))

            part_i = Particle(f"Particella_{i}", P_i, mass)

            punti.append(P_i)
            particelle.append(part_i)
    return particelle, punti, transformations


@app.cell(hide_code=True)
def _(N, O, mo, n_particelle, particelle, vlatex):
    listapunti = [
        mo.md(
            rf"""$$OP_{i + 1} = {
                vlatex(m_point.point.pos_from(O).to_matrix(N))
            }, \quad {vlatex(m_point.mass)} $$"""
        ).center()
        for i, m_point in filter(lambda x : x[1].mass != 0, enumerate(particelle))
    ]
    mo.vstack([mo.md("**List of points**:"),
    mo.vstack([
        mo.hstack([
            listapunti[j] for j in range(i*3, min(len(listapunti), (i+1)*3))
        ]) for i in range((n_particelle.value // 3) + 1)
    ])])
    return


@app.cell(hide_code=True)
def _(N, mo, n_particelle, particelle, vlatex):
    listavelocity = [
        mo.md(
            rf"""$$OP_{i + 1} = {
                vlatex(m_point.point.vel(N).to_matrix(N))
            }, \quad {vlatex(m_point.mass)} $$"""
        ).center()
        for i, m_point in filter(lambda x : x[1].mass != 0, enumerate(particelle))
    ]
    mo.vstack([mo.md("**Vectors velocities**:"),
    mo.vstack([
        mo.hstack([
            listavelocity[j] for j in range(i*3, min(len(listavelocity), (i+1)*3))
        ]) for i in range((n_particelle.value // 3) + 1)
    ])])
    return


@app.cell(hide_code=True)
def _(N, O, mo, n_particelle, particelle, vlatex):
    geometricpoints = [
        mo.md(
            rf"""$$OP_{i + 1} = {
                vlatex(m_point.point.pos_from(O).to_matrix(N))
            }, \quad {vlatex(m_point.mass)} $$"""
        ).center()
        for i, m_point in filter(lambda x: x[1].mass == 0, enumerate(particelle))
    ]
    mo.vstack(
        [
            mo.md("""**List of "geometric" points** 

    (points without mass, they can be the anchor of other elements like bars, sprins, ...):"""),
            mo.vstack(
                [
                    mo.hstack(
                        [
                            geometricpoints[j]
                            for j in range(
                                i * 3, min(len(geometricpoints), (i + 1) * 3)
                            )
                        ]
                    )
                    for i in range((n_particelle.value // 3) + 1)
                ]
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Potentials
    """)
    return


@app.cell(hide_code=True)
def _(N, O, mo, particelle, s, simplify):
    def gravitational(P, g = s.g, direction = 1, origin = O, reference = N):
        vertical = N.y * direction
        r = P.point.pos_from(O)
        return g * P.mass * r.dot(vertical)

    V_gravi = simplify(sum([gravitational(P) for P in particelle]))

    mo.md(r"""
    ## Gravitational
    The default is to consider the $y$ axis to point upwards
    $$
    V_{gravi}(OP) = m\cdot g \cdot OP_y
    $$""")
    return (V_gravi,)


@app.cell(hide_code=True)
def _(V_gravi, mo, simplify, vlatex):
    mo.md(rf"""
    in this case the total gravitatinal potential is
              \[{vlatex(V_gravi)}\]
    which simplifies to 
              \[{vlatex(simplify(V_gravi))}\]
    """)
    return


@app.cell(hide_code=True)
def _(N, O, mo):
    def centrifugal(P, omega, axis=0 * N.x, origin=O):
        if axis.dot(axis) == 0:
            return 0
        r = P.point.pos_from(origin)
        r_ort = r.cross(axis)

        # Modulo quadro della distanza dall'asse
        d2 = r_ort.dot(r_ort) / axis.dot(axis)

        return -P.mass * omega**2 * d2 / 2


    axis = mo.md("""### Axis\n If you leave a null vector, then the function will return centrifugal potential equal to $0$\n
            {X} {Y} {Z}
            """).batch(
        X=mo.ui.text(label="X", value="0", placeholder="pos x"),
        Y=mo.ui.text(label="Y", value="0", placeholder="pos y"),
        Z=mo.ui.text(label="Z", value="0", placeholder="pos z"),
    )

    mo.md(r"""
    ## Centrifugal
    * $d\quad$ is the distance of the point $OP$ from the rotating axis
    * $\omega\quad$ is the angular velocity
    $$
    V_{centr}(OP) = - \frac{\omega^2}{2} \cdot m \cdot d^2
    $$
    """)
    return axis, centrifugal


@app.cell(hide_code=True)
def _(axis):
    axis
    return


@app.cell(hide_code=True)
def _(
    N,
    axis,
    centrifugal,
    dict_simboli,
    mo,
    parse_expr,
    particelle,
    s,
    simplify,
    transformations,
    vlatex,
):
    X_axis, Y_axis, Z_axis = [
        parse_expr(
            str_input, local_dict=dict_simboli, transformations=transformations
        )
        for str_input in axis.value.values()
    ]
    rotational_ax = X_axis * N.x + Y_axis * N.y + Z_axis * N.z
    V_centr = (
        sum([centrifugal(P, s.omega, rotational_ax) for P in particelle])
    )
    mo.vstack([
        mo.md(rf"""in this case the total centrifugal potential with axis 
        of rotation the vector
        \[{vlatex(rotational_ax.to_matrix(N))}\] is""")
    , mo.center(V_centr), mo.md(f"which simplifies to"), simplify(V_centr)])
    return (V_centr,)


@app.cell(hide_code=True)
def _(mo, s):
    def elastic(spring, punti, k=s.k):
        if spring is None:
            return 0
        if spring[0] >= len(punti) or spring[1] >= len(punti):
            return 0
        r = punti[spring[0]].pos_from(punti[spring[1]])
        return r.dot(r) * k / 2


    n_springs = mo.ui.number(
        start=0, stop=20, step=1, value=1, label="Number of springs"
    )
    mo.vstack(
        [
            mo.md(r"""
            ## Elastic
            of a spring applied between points $OP$ and $OQ$
            $$
            V_{elast}(QP) = k\cdot\frac{|QP|^2}{2}
            $$
            """
            ),
            n_springs,
        ]
    )
    return elastic, n_springs


@app.cell(hide_code=True)
def _(mo, n_particelle, n_springs):
    # 1. Costruiamo dinamicamente l'intestazione e le righe di una tabella Markdown
    md_table = "| Spring | First point | Second point |\n|:---:|:---:|:---:|\n"
    for j in range(1,n_springs.value+1):
        md_table += f"| **{j}** | {{idx1_{j}}} | {{idx2_{j}}} |\n"

    # 2. Prepariamo un dizionario contenente tutti i widget
    # Le chiavi devono corrispondere esattamente ai placeholder {nome} usati nel Markdown
    input_widgets = {}
    for j in range(1,n_springs.value+1):
        input_widgets[f"idx1_{j}"] = mo.ui.number(1, n_particelle.value, value=1, step=1)
        input_widgets[f"idx2_{j}"] = mo.ui.number(1, n_particelle.value, value=1, step=1)

    # 3. Generiamo l'elemento UI unificato
    # .batch() prende i widget e li inietta nel layout, rendendo il tutto un unico blocco reattivo
    tabella_indici = mo.md(md_table).batch(**input_widgets)

    # Visualizzazione (sarà una classica tabella HTML pulita)
    mo.vstack([mo.md("### Springs"), tabella_indici])
    return (tabella_indici,)


@app.cell(hide_code=True)
def _(elastic, mo, n_springs, punti, simplify, tabella_indici):
    springs = [
        (
            tabella_indici.value[f"idx1_{j}"] - 1,
            tabella_indici.value[f"idx2_{j}"] - 1,
        )
        for j in range(1, n_springs.value + 1)
    ]

    V_elast = simplify(sum([elastic(spring, punti) for spring in springs]))
    mo.vstack(
        [
            mo.md("given the springs between the points:"),
            mo.hstack(
                [
                    mo.md(
                        rf"$OP_{{{x[0]}}} \leftrightarrow OP_{{{x[1]}}}$"
                    ).center()
                    for x in springs
                ]
            ),
            mo.md(f"in this case the total elastic potential is"),
            mo.center(V_elast),
            mo.md(f"which simplifies to"),
            simplify(V_elast),
        ]
    )
    return (V_elast,)


@app.cell(hide_code=True)
def _(Matrix, V_centr, V_elast, V_gravi, mo, q, simplify):
    V_tot = simplify(V_centr + V_elast + V_gravi)
    V_grad = simplify(Matrix([V_tot]).jacobian(q).T)
    mo.vstack(
        [
            mo.md(r"""
            # Equilibria
            Consider the total potential 
            (ignore the terms that not apply to the current case) 
            \[V_{tot} = V_{centr} + V_{elast} + V_{gravi}\]"""),
            mo.md("In thise case the total potential is: "),
            V_tot,
            mo.md("which gradient in the lagrangian coordinates is"),
            V_grad,
            mo.md("The Hessian of the potential is"),
            simplify(V_grad.jacobian(q))
        ]
    )
    return V_grad, V_tot


@app.cell
def _(V_grad, q, sm):
    # This cell makes the heavy lift, do not re-run if unnecessary
    equilibria = sm.solve(list(V_grad), list(q))
    return (equilibria,)


@app.cell(hide_code=True)
def _(V_grad, equilibria, mo, q, simplify, vlatex):
    V_hess = simplify(V_grad.jacobian(q))
    hessians = [V_hess.subs(dict(zip(list(q), eq))) for eq in equilibria]

    # 1. Costruiamo dinamicamente l'intestazione e le righe di una tabella Markdown
    eq_md_table = """| Equilibrium | coordinates | Hessian positivity | Determinant | Trace |
        |:---:|:---:|:---:|:---:|:---:|\n"""
    for je, eq in enumerate(equilibria):
        hess_sign = "?"
        H = hessians[je]
        if H.is_positive_semidefinite:
            hess_sign = r"\ge"
            if H.is_positive_definite:
                hess_sign = r">"
        elif H.is_negative_semidefinite:
            hess_sign = r"\le"
            if H.is_positive_definite:
                hess_sign = "<"

        eq_md_table += f"""|**{je}**|${vlatex(eq)}$|${hess_sign}$|${vlatex(H.det())}$|${vlatex(H.trace())}$|\n"""

    # Visualizzazione (sarà una classica tabella HTML pulita)
    mo.vstack([mo.md("### Equilibria"), mo.md(eq_md_table)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *NOTE* 👀

    If you see $?$ in the *Hessian positivity* column that means that the solver cannot decide the sign of the eigenvalues of the Hessian. That happens when the signs of the eigenvalues depends on one or more relations between the paramters (something like $gm > kl$ for example), which necessitates a discussion

    The same can happen with the equilibria: the solver does return equilibrium like $\sqrt{\alpha - 1}$ without specifying that for some values of $\alpha$ this equilibrium does not exists.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    📝 Recall that
    - Determinant is the product of the eigenvalues
    - Trace (sum of the diagonal elements of a matrix) is the sum of the eigenvalues

    therefore
    - negative determinant implies the presence of eigenvalues of different signs (at leas one is negative) => **INstability**
    - positive determinant implies that the eigenvalues have the same sign
        - if the trace is positive, they are both positive => **stability**
        - if the trace is negative, they are both negative => **INstability**
    - determinant equals to zero
        - if the trace is negative, the only eigenvalue is negative => **INstability**
        - if the trace is positive, you cannot conclude
        - if the trace is null, you cannot conclude
    """)
    return


@app.cell(hide_code=True)
def _(N, mo, particelle):
    K = (
        sum([OP.mass * OP.point.vel(N).dot(OP.point.vel(N)) for OP in particelle])
        / 2
    )
    mo.vstack(
        [
            mo.md(r"""
            # Kinetic energy
            The total kinetic energy of a system of $N$ mass points is
            \[ K = \frac{1}{2} \sum_{j=1}^N m_j\cdot |v_j|^2\]
            where $|v_i|$ is the modulo of the velocity of point $j$.
            """)
        ]
    )
    return (K,)


@app.cell(hide_code=True)
def _(K, mo, qd, simplify, sm):
    mo.vstack(
        [
            mo.md("In this case the total kinetic energy is"),
            mo.center(K),
            mo.md(f"which simplifies to"),
            simplify(K),
            mo.md("The associated quadratic form is:"),
            simplify(sm.hessian(K, qd))
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lagrange equations
    $$
    \frac{d}{dt} \frac{\partial L}{\partial \dot{q}_i} -  \frac{\partial L}{\partial q_i} = 0 \quad i=1,\dots,m
    $$
    """)
    return


@app.cell(hide_code=True)
def _(K, Matrix, V_tot, mo, q, qd, simplify, t, vlatex):
    L = simplify(K - V_tot)
    ML = Matrix([L])
    ML_dq = ML.jacobian(qd).T
    ML_q = ML.jacobian(q).T
    mo.vstack(
        [
            mo.md(r"Partial derivative with respect to $\dot{q}$"),
            mo.hstack(
                [
                    mo.md(r"\[\frac{\partial L}{\partial \dot{q}_i}\]").center(),
                    mo.vstack(
                        [
                            mo.hstack([
                                mo.md(rf""" \[\dot{{q}}_{i} =  {vlatex(lq)}\]"""),
                                mo.md(rf""" \[{vlatex(ML_dq[i])}\]""").center()])
                            for i, lq in enumerate(q)
                        ]
                    ),
                ]
            ),
            mo.md("\nNow the time derivative\n"),
            mo.hstack(
                [
                    mo.md(r"""\[\frac{d}{dt}
                    \frac{\partial L}{\partial \dot{q}_i}\]""").center(),
                    mo.vstack(
                        [
                            mo.hstack(
                                [
                                    mo.md(rf""" \[\dot{{q}}_{i} =  {vlatex(lq)}\]"""),
                                    mo.md(
                                        rf""" \[{vlatex(ML_dq[i].diff(t))}\]"""
                                    ).center(),
                                ]
                            )
                            for i, lq in enumerate(q)
                        ]
                    ),
                ]
            ),
            mo.md(r"Partial derivative with respect to $q$"),
            mo.hstack(
                [
                    mo.md(r"""\[\frac{\partial L}{\partial q_i}\]""").center(),
                    mo.vstack(
                        [
                            mo.hstack(
                                [
                                    mo.md(rf""" \[q_{i} =  {vlatex(lq)}\]"""),
                                    mo.md(rf""" \[{vlatex(ML_q[i])}\]""").center(),
                                ]
                            )
                            for i, lq in enumerate(q)
                        ]
                    ),
                ]
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
