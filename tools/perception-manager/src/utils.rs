use ssh2::Session;
use std::error::Error;
use std::net::{TcpStream, ToSocketAddrs};
use std::time::Duration;

pub fn connect(a: &str) -> Result<Session, Box<dyn Error>> {
    let socket_address = format!("{}:22", a)
        .to_socket_addrs()?
        .next()
        .ok_or("Unable to resolve address")?;
    let tcp = TcpStream::connect_timeout(&socket_address, Duration::new(5, 0))?;
    let mut sess = Session::new().unwrap(); // You might consider handling this error as well.
    sess.set_tcp_stream(tcp);
    sess.handshake()?;
    sess.userauth_password("ubuntu", "peninsula")?;

    Ok(sess)
}
