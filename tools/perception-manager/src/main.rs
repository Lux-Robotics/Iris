mod utils;

use eframe::{egui, Theme};
use ssh2::Session;

#[derive(Default)]
struct MyEguiApp {
    ip_input: String,
    status: String,
    sess: Option<Session>,
}

impl MyEguiApp {
    fn new(cc: &eframe::CreationContext<'_>) -> Self {
        // Customize egui here with cc.egui_ctx.set_fonts and cc.egui_ctx.set_visuals.
        // Restore app state using cc.storage (requires the "persistence" feature).
        // Use the cc.gl (a glow::Context) to create graphics shaders and buffers that you can use
        // for e.g. egui::PaintCallback.
        MyEguiApp {
            ip_input: "10.60.36.11".to_string(),
            status: "Not Connected".to_string(),
            ..Default::default()
        }
    }
}

impl eframe::App for MyEguiApp {
    fn update(&mut self, ctx: &egui::Context, frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.label("IP Address:");
            ui.text_edit_singleline(&mut self.ip_input);
            ui.label(&self.status);
            if ui.button("Click me").clicked() {
                self.status = "Connecting".to_string();
                ctx.request_repaint();
                let sess = utils::connect(&self.ip_input);
                self.status = match sess {
                    Ok(s) => {
                        self.sess = Some(s);
                        "Connected to ".to_string() + &self.ip_input
                    }
                    Err(e) => {
                        self.sess = None;
                        e.to_string()
                    }
                };
                println!("{}", self.status);
            }
        });
    }
}

fn main() {
    let native_options = eframe::NativeOptions::default();
    eframe::run_native(
        "Perception Manager",
        native_options,
        Box::new(|cc| Box::new(MyEguiApp::new(cc))),
    );
}
