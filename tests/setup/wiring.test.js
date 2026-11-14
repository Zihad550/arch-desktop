// Arch installer wiring, asserted against source text.
//
//     node --test tests/setup/wiring.test.js
//
// Setup scripts have no safe in-container runtime harness, so these checks pin
// source structure. Headless installer checks live in dotfiles'
// tests/setup/headless.test.js.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "../..");

function source(relativePath) {
    return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

test("both Arch profiles install Herdr with pacman", () => {
    const devbox = source("setup/common/packages/pacman-base");
    const workstation = source("setup/arch-workstation/packages/pacman-base");

    assert.match(devbox, /^\s*herdr \\/m);
    assert.match(workstation, /^\s*herdr$/m);
    assert.doesNotMatch(workstation, /mise (unuse|uninstall)|rm -[fr]+[^\n]*herdr/);
});

test("Arch workstation is a remote-development client", () => {
    const init = source("setup/arch-workstation/init");
    const packages = source("setup/arch-workstation/packages/pacman-base");
    const apps = source("setup/arch-workstation/packages/pacman-apps");
    const flatpaks = source("setup/common/packages/flatpak-packages");
    const stow = source("setup/arch-workstation/stow");
    const syncthing = source("setup/arch-workstation/setup-packages/setup-syncthing");
    const ufw = source("setup/arch-workstation/setup-packages/setup-ufw");
    const workstationGitHub = source("setup/arch-workstation/setup-packages/setup-github-cli");
    const devboxGitHub = source("setup/arch-devbox/setup-github-cli");

    assert.doesNotMatch(init,
        /setup-rootless-docker|go-packages|setup-file-watchers|setup-ts-serve|df-gen-completions/);
    assert.doesNotMatch(packages,
        /^\s*(gcc|base-devel|docker|docker-compose|go|nodejs|npm|pnpm|python|rust)(?:\s|\\|$)/m);
    assert.match(packages, /^\s*openssh \\/m);
    assert.match(packages, /^\s*tailscale \\/m);
    assert.match(packages, /^\s*herdr$/m);
    assert.match(packages, /^\s*github-cli \\/m);
    assert.match(packages, /systemctl enable --now tailscaled\.service/);
    assert.match(apps, /^\s*zed \\/m);
    assert.match(apps, /^\s*neovim \\/m);
    assert.match(apps, /^\s*helium-browser-bin \\/m);
    assert.doesNotMatch(init, /packages\/yay-packages/);
    assert.doesNotMatch(apps, /dragon-drop/);
    assert.match(apps, /^\s*yazi resvg \\/m);
    assert.doesNotMatch(`${init}\n${packages}\n${apps}\n${flatpaks}`,
        /(^|\s)chromium(?:\s|\\|$)/m);
    assert.match(flatpaks, /com\.mongodb\.Compass/);
    assert.match(flatpaks, /io\.beekeeperstudio\.Studio/);
    assert.match(stow, /^stow .* zed$/m);
    assert.match(stow, /^stow .* kanata$/m);
    assert.match(stow, /^stow .* dotfiles$/m);
    assert.match(init, /setup\/common\/setup-kanata/);
    assert.match(init, /setup-packages\/setup-syncthing/);
    assert.match(syncthing, /systemctl --user enable --now syncthing\.service/);
    assert.doesNotMatch(syncthing, /~\/dev|\.stignore_dev/);
    assert.match(ufw, /sudo ufw deny SSH/);
    assert.doesNotMatch(ufw, /ufw allow (SSH|syncthing)/);
    assert.doesNotMatch(init, /systemctl[^\n]*sshd|run_step[^\n]*sshd/);
    assert.match(workstationGitHub, /gh config set git_protocol ssh/);
    assert.match(workstationGitHub, /gh extension install dlvhdr\/gh-dash/);
    assert.doesNotMatch(devboxGitHub, /gh config set git_protocol/);
    assert.match(devboxGitHub, /gh extension install dlvhdr\/gh-dash/);
    assert.doesNotMatch(stow, /stow (git|lazygit|worktrunk)|stow-ai/);
});

test("both Arch profiles install Claude Desktop with pacman", () => {
    for (const profile of ["arch-workstation", "arch-devbox"]) {
        assert.match(source(`setup/${profile}/packages/pacman-apps`), /^\s*claude-desktop(?:\s|\\|$)/m);
    }
    assert.doesNotMatch(source("setup/arch-devbox/packages/yay-packages"), /claude-desktop/);
});

test("Arch devbox excludes workstation sync", () => {
    const init = source("setup/arch-devbox/init");
    const packages = [
        source("setup/common/packages/pacman-base"),
        source("setup/arch-devbox/packages/pacman-apps"),
        source("setup/arch-devbox/packages/yay-packages"),
    ].join("\n");

    assert.doesNotMatch(init, /run_step[^\n]*syncthing/i);
    assert.doesNotMatch(packages, /^\s*syncthing(?:\s|\\|$)/m);
    assert.doesNotMatch(init, /setup\/common\/packages\/yay-packages/);
    assert.match(packages, /^\s*yazi resvg \\/m);
    assert.match(packages, /dragon-drop/);
});

test("Arch workstation keeps development tools inside devvm", () => {
    const init = source("setup/arch-workstation/init");
    assert.doesNotMatch(init, /setup-mise|mise-dev-packages|setup-skills/);
    assert.match(init, /run_step "devvm" "\$ARCH_DESKTOP_DIR\/setup\/common\/setup-devvm"/);
});

test("Arch devbox installs mise and skills before devvm", () => {
    assert.ok(fs.existsSync(path.join(repoRoot, "setup/common/setup-mise")));
    const init = source("setup/arch-devbox/init");
    assert.match(init,
        /run_step "mise" "\$ARCH_DESKTOP_DIR\/setup\/common\/setup-mise"[\s\S]*run_step "mise packages"[\s\S]*run_step "skills"/);
    assert.match(init, /join_lane tools[\s\S]*run_step "devvm"/);
});

test("Arch installers call the shared helpers through the portable checkout", () => {
    for (const profile of ["arch-workstation", "arch-devbox"]) {
        const init = source(`setup/${profile}/init`);
        for (const helper of ["check-machine-profile", "hw-detect", "set-dotfiles-profile"]) {
            assert.match(init, new RegExp(`"\\$ARCH_DESKTOP_DIR/portable/setup/common/${helper}"`),
                `${profile} does not reach ${helper} in dotfiles`);
            assert.ok(fs.existsSync(path.join(repoRoot, "portable/setup/common", helper)), `${helper} is missing`);
        }
        assert.doesNotMatch(init, /\$ARCH_DESKTOP_DIR\/setup\/common\/(check-machine-profile|hw-detect|set-dotfiles-profile|setup-herdr)\b/);
    }
    assert.match(source("setup/arch-devbox/init"), /run_step "herdr" "\$ARCH_DESKTOP_DIR\/portable\/setup\/common\/setup-herdr"/);
    assert.match(source("setup/boot.sh"), /"\$DOTFILES_DIR\/setup\/common\/check-machine-profile" "\$target"/);
});

test("Arch installers persist their machine profile after post-install", () => {
    const workstation = source("setup/arch-workstation/init");
    const devbox = source("setup/arch-devbox/init");

    assert.match(workstation,
        /run_step "post-install"[\s\S]*run_step "machine profile"[^\n]*arch-workstation[\s\S]*touch "\$ARCH_SETUP_STATE_DIR\/\.initialized"/);
    assert.match(devbox,
        /run_step "post-install"[\s\S]*run_step "machine profile"[^\n]*arch-devbox[\s\S]*touch "\$ARCH_SETUP_STATE_DIR\/\.initialized"/);
});

test("both Arch profiles install the shared power-button policy", () => {
    for (const relativePath of ["setup/arch-workstation/init", "setup/arch-devbox/init"]) {
        assert.match(source(relativePath),
            /run_step "power button" "\$ARCH_DESKTOP_DIR\/setup\/common\/setup-power-button-suspend"/,
            `${relativePath} does not install the shared power-button policy`);
    }
});

test("Arch devbox installs DNS after the base packages", () => {
    assert.match(source("setup/arch-devbox/init"),
        /run_step "pacman base"[^\n]*\nrun_step "DNS" "\$ARCH_DEVBOX_DIR\/setup-dns"$/m);
});

test("generated completions replace shell-startup generators", () => {
    const generator = source("portable/bin/df-gen-completions");
    const zshrc = source("portable/zsh/.config/zsh/.zshrc");
    const setupMise = source("setup/common/setup-mise");

    assert.match(generator, /^gen mise mise completion zsh$/m);
    assert.match(generator, /^gen kubectl kubectl completion zsh$/m);
    assert.match(generator, /^gen herdr herdr completion zsh$/m);
    assert.doesNotMatch(generator, /^gen devvm /m);
    assert.doesNotMatch(source("setup/arch-workstation/setup-completions"), /devvm/);
    assert.match(zshrc, /if commands_available devvm; then eval "\$\(devvm completion zsh\)"; fi/);
    assert.doesNotMatch(zshrc, /kubectl completion zsh|herdr completion zsh/);
    assert.doesNotMatch(setupMise, /mise completion zsh|site-functions/);
});

test("the ADR records completed feasibility and per-host runtime checks", () => {
    const adr = source("docs/adr/0029-headless-profiles-use-herdr.md");

    assert.match(adr, /Alpine[\s\S]*feasibility check passed/i);
    assert.match(adr, /verified[\s\S]*Ubuntu devbox, Ubuntu server,[\s\S]*and Alpine/i);
});

