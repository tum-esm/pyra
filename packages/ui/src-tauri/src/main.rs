use std::process::Command;

#[cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

// TODO: Set corrent path on windows/unix (Fixed path required on every system)

fn call_pyra_cli(argument_string: &str) -> Result<std::process::Output, std::io::Error> {
  let project_dir = String::from("/Users/moritz/Documents/research/pyra");
  let pyra_venv = format!("{}/.venv/bin/python", project_dir);
  let pyra_cli_main = format!("{}/packages/cli/main.py", project_dir);
  Command::new(pyra_venv)
    .arg(pyra_cli_main)
    .args(argument_string.to_string().split(" "))
    .output().into()
}

#[tauri::command]
fn pyra_cli_is_available() -> bool {
  let output_result = call_pyra_cli("--help");
  match output_result {
    Ok(v) => v.stdout.starts_with(b"Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...").into(),
    Err(_e) => false.into(),
  }
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![pyra_cli_is_available])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
