"""Retroalimentación formativa portable para misiones evaluables."""

PHYSICAL_VALIDATION_NOTICE = (
    "Esta evidencia proviene del simulador. Valida el programa también en un robot EV3 físico "
    "antes de una demostración o evaluación final."
)


def formative_mission_feedback(*, outcome: str, result: dict[str, object]) -> dict[str, str]:
    """Convierte el resultado técnico en una orientación honesta para aprender."""

    if outcome == "finished" and bool(result.get("passed")):
        summary = "Lograste los criterios observables de esta práctica en el simulador."
        next_step = "Repite la práctica cambiando un parámetro y compara la nueva telemetría."
    elif outcome == "cancelled":
        summary = "La práctica fue cancelada antes de reunir toda su evidencia."
        next_step = "Reinicia, ejecuta de nuevo y observa cada criterio antes de detenerla."
    elif outcome == "timed_out":
        summary = "La práctica alcanzó el tiempo máximo configurado."
        next_step = "Revisa bucles y esperas; aumenta el límite solo si la misión lo necesita."
    elif outcome == "error":
        summary = "El programa terminó con un error y la práctica no puede validarse todavía."
        next_step = "Lee el error del editor, corrígelo y usa depuración paso a paso si es necesario."
    else:
        summary = "Aún no se cumplieron todos los criterios observables de la práctica."
        next_step = "Compara los criterios no superados con el mundo, el script y la telemetría."
    return {
        "summary": summary,
        "next_step": next_step,
        "physical_validation_notice": PHYSICAL_VALIDATION_NOTICE,
    }
