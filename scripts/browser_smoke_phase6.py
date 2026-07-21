"""Smoke responsivo e de acessibilidade em navegadores reais via Playwright."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright


MENUS = ("Escalação", "Scout", "Jogadores", "Indicadores")
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 390, "height": 844},
}


def _assert_basico(page: Page, *, menu: str, viewport: str) -> dict[str, object]:
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)

    title = page.title()
    body_text = page.locator("body").inner_text()
    if "O Caminho para o Hexa" not in body_text:
        raise AssertionError(f"Título do projeto ausente em {menu}/{viewport}.")
    if page.locator("h1").count() < 1:
        raise AssertionError(f"Nenhum h1 encontrado em {menu}/{viewport}.")

    duplicados = page.evaluate(
        """() => {
            const ids = [...document.querySelectorAll('[id]')].map((el) => el.id);
            return ids.filter((id, index) => id && ids.indexOf(id) !== index);
        }"""
    )
    if duplicados:
        raise AssertionError(f"IDs duplicados em {menu}/{viewport}: {duplicados}")

    imagens_sem_alt = page.evaluate(
        """() => [...document.querySelectorAll('img')]
            .filter((img) => !img.hasAttribute('alt'))
            .map((img) => img.src)"""
    )
    if imagens_sem_alt:
        raise AssertionError(
            f"Imagens sem texto alternativo em {menu}/{viewport}: {imagens_sem_alt}"
        )

    controles_sem_nome = page.evaluate(
        """() => [...document.querySelectorAll(
            'button, input, select, textarea, [role="button"]'
        )].filter((el) => {
            if (el.getAttribute('aria-hidden') === 'true') return false;
            const nome = (
                el.getAttribute('aria-label') ||
                el.getAttribute('title') ||
                el.innerText ||
                el.value ||
                ''
            ).trim();
            return !nome;
        }).length"""
    )

    largura = page.evaluate(
        """() => ({
            viewport: document.documentElement.clientWidth,
            documento: document.documentElement.scrollWidth,
        })"""
    )
    excesso = int(largura["documento"]) - int(largura["viewport"])
    if excesso > 8:
        raise AssertionError(
            f"Overflow horizontal global de {excesso}px em {menu}/{viewport}."
        )

    erros_streamlit = page.locator('[data-testid="stException"]').count()
    if erros_streamlit:
        raise AssertionError(f"Exceção Streamlit visível em {menu}/{viewport}.")

    return {
        "menu": menu,
        "viewport": viewport,
        "title": title,
        "h1": page.locator("h1").count(),
        "controles_sem_nome": controles_sem_nome,
        "overflow_px": excesso,
    }


def _abrir_menu(page: Page, menu: str, *, mobile: bool) -> None:
    if mobile:
        botao_sidebar = page.locator('[data-testid="stSidebarCollapsedControl"]')
        if botao_sidebar.count():
            botao_sidebar.first.click()
            page.wait_for_timeout(300)

    opcao = page.get_by_text(menu, exact=True)
    if not opcao.count():
        raise AssertionError(f"Menu não encontrado: {menu}")
    opcao.first.click()
    page.wait_for_timeout(900)


def executar(browser: Browser, base_url: str, output_dir: Path) -> list[dict[str, object]]:
    resultados: list[dict[str, object]] = []
    for viewport_nome, viewport in VIEWPORTS.items():
        contexto = browser.new_context(
            viewport=viewport,
            device_scale_factor=1,
            locale="pt-BR",
            color_scheme="dark",
            reduced_motion="reduce",
        )
        page = contexto.new_page()
        page.goto(base_url, wait_until="networkidle")
        page.wait_for_timeout(1200)

        for menu in MENUS:
            _abrir_menu(page, menu, mobile=viewport_nome == "mobile")
            resultado = _assert_basico(
                page,
                menu=menu,
                viewport=viewport_nome,
            )
            resultados.append(resultado)
            nome = f"{viewport_nome}-{menu.casefold().replace('ç', 'c').replace(' ', '-')}.png"
            page.screenshot(path=str(output_dir / nome), full_page=True)

        contexto.close()
    return resultados


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument(
        "--browser",
        choices=("chromium", "firefox", "webkit"),
        default="chromium",
    )
    parser.add_argument("--output", default="artifacts/browser-phase6")
    parser.add_argument("--executable-path", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        tipo = getattr(playwright, args.browser)
        launch_args = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-software-rasterizer", "--single-process"]}
        if args.executable_path:
            launch_args["executable_path"] = args.executable_path
        browser = tipo.launch(**launch_args)
        try:
            resultados = executar(browser, args.url, output_dir)
        finally:
            browser.close()

    (output_dir / f"resultado-{args.browser}.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Browser smoke: OK; navegador={args.browser}; "
        f"cenários={len(resultados)}"
    )


if __name__ == "__main__":
    main()
