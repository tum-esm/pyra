use std::process::Command;

#[cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

// TODO: Set corrent path on windows/unix (Fixed path required on every system)
fn call_pyra_cli_arraywise(argument_vector: Vec<&str>) -> Result<std::process::Output, std::io::Error> {
  let project_dir = String::from("/Users/moritz/Documents/research/pyra");
  let pyra_venv = format!("{}/.venv/bin/python", project_dir);
  let pyra_cli_main = format!("{}/packages/cli/main.py", project_dir);
  println!("calling pyra-cli with args: {:?}", argument_vector);
  Command::new(pyra_venv).arg(pyra_cli_main).args(argument_vector).output().into()
}

#[tauri::command]
fn cli_is_available() -> bool {
  let output_result = call_pyra_cli_arraywise(["--help"].to_vec());
  match output_result {
    Ok(v) => v.stdout.starts_with(b"Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...").into(),
    Err(_e) => false.into(),
  }
}

#[tauri::command]
fn read_info_logs() -> String {
  let output_result = call_pyra_cli_arraywise(["logs", "read", "--level", "INFO"].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

#[tauri::command]
fn read_debug_logs() -> String {
  let output_result = call_pyra_cli_arraywise(["logs", "read", "--level", "DEBUG"].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

#[tauri::command]
fn archive_logs() -> String {
  let output_result = call_pyra_cli_arraywise(["logs", "archive"].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

#[tauri::command]
fn read_setup_json() -> String {
  let output_result = call_pyra_cli_arraywise(["config", "setup", "get"].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

#[tauri::command]
fn read_parameters_json() -> String {
  let output_result = call_pyra_cli_arraywise(["config", "parameters", "get"].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

#[tauri::command]
fn update_setup_json(new_json_string: String) -> String {
  let output_result = call_pyra_cli_arraywise([
    "config",
    "setup", 
    "update",
    "--content",
    &(new_json_string.replace("\\\"", "\""))
  ].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "nope".into(),
  }
}

#[tauri::command]
fn update_parameters_json(new_json_string: String) -> String {
  let output_result = call_pyra_cli_arraywise([
    "config",
    "parameters", 
    "update",
    "--content",
    &(new_json_string.replace("\\\"", "\""))
  ].to_vec());
  match output_result {
    Ok(v) => String::from_utf8(v.stdout).unwrap().into(),
    Err(_e) => "".into(),
  }
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
      cli_is_available,
      read_info_logs,
      read_debug_logs,
      archive_logs,
      read_setup_json,
      read_parameters_json,
      update_setup_json,
      update_parameters_json
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
