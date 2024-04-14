    /** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";

var cancel = true;
var paymentSocket;

var DEBUG = true; // set to false to disable debugging
var old_console_log = console.log;
console.log = function () {
    if (DEBUG) {
        old_console_log.apply(this, arguments);
    }
}

export class PaymentTerminal extends PaymentInterface {

    /**
     * @override
     */
    send_payment_request(cid) {
        console.log("--------------------------------------------\n" +
                    "REALIZANDO LA ACCION DE PAGO POR SMARTCASH\n" +
                    "--------------------------------------------");
        var line = this.pos.get_order().selected_paymentline;
        var order = this.pos.get_order();
        var data = this._terminal_pay_data();
        var Recript_no = this.pos.get_order().name;
        var Login_user = this.pos.get_cashier().name;
        var Pos_name = this.pos.config.name;
        var Gateway_ip = this.pos.config.gateway_ip;
        var Port_ip = this.pos.config.port_ip;
        var directPrint = this.pos.config.direct_print_receipt; 

        console.log("CONECTANDO A LA IP: " , Gateway_ip);
        console.log("APUNTANDO AL PUERTO: ", Port_ip);

        try {
            paymentSocket = new WebSocket ("wss://"+Gateway_ip+":"+Port_ip+"");    
        } catch (error) {
            alert("No se han configurado los datos de la pasarela.");
            line.set_payment_status('retry');    
            return;           
        }
        
        var dataTime = this._current_time_date();
        var price = parseInt(data.RequestedAmount*100);
        var mensaje = 'DATA;' + data.OrderID +'-'+ dataTime + ';' + Login_user  + ';' + Pos_name + ';' + price + ';' + 1 + ';' + 0;
        
        console.log('Price: ' + price);
        console.log('Mensaje de pago: ' + mensaje);
        var success = false;
        var error = false;
        var response = 0;
        cancel = false;
        
        

        paymentSocket.onopen = function (event) {
            sendMessage(paymentSocket, mensaje);
            console.log("--------------------------\n" +	
                        "SE ENVIA EL PAGO A IMACASH\n" +
                        "--------------------------");    
        }

        paymentSocket.onmessage = function (event) {
            console.log(event);
            var reader = new FileReader();
            response = ++response;
            console.log("Numero del mensaja recibido: " , response);

            reader.addEventListener("loadend", function() {
                
                var recieved = reader.result;
                console.log("Mensaje recibido de imacash: " , recieved);
                var code = recieved.substr(recieved.length - 3);
                console.log("Code: ", code);

                if (code == '000'){
                    if (response == 2 && !cancel){
                        console.log('PAGO REALIZADO CON EXITO');
                        success = true;
                    }else{
                        console.log('Recibido');
                    }
                } else if (code == '001'){
                    console.log('PAGO CANCELADO');
                    error = true;

                }else{
                    console.log('ERROR!');
                    error = true;
                }

                if(success){
                    // You can send your request from here to the terminal, and based on the response from your
                    // terminal you can set payment_status to success / retry / waiting.
                    console.log("Done");
                    line.set_payment_status('done');
                    if (directPrint) {
                        $('.button.next').click();
                    }
                }else if(error) {
                    console.log("Retry");
                    line.set_payment_status('retry');
                }else{
                    console.log("Waiting")
                    line.set_payment_status('waiting');
                }

                paymentSocket.onclose = function (event) {
                    console.log(event);
                    console.log("CERRANDO SOCKET PAGAR");
                        if (response < 1)
                            alert("La pasarela no esta disponible o no responde.");
                    //line.set_payment_status('retry');
                };
    
                paymentSocket.onerror = function (event) {
                    console.log("ERROR EN EL SOCKET");
                    console.log(event);
                    alert("Error en la conexion");             
                };

                reader.abort();
            });

            reader.readAsText(event.data);
            
        };

        //Wait for the WebSocket connection to be open, before sending a message.
        const waitForOpenConnection = (socket) => {
            return new Promise((resolve, reject) => {
                const maxNumberOfAttempts = 10
                const intervalTime = 200 //ms
        
                let currentAttempt = 0
                const interval = setInterval(() => {
                    if (currentAttempt > maxNumberOfAttempts - 1) {
                        clearInterval(interval)
                        reject(new Error('Maximum number of attempts exceeded'))
                    } else if (socket.readyState === socket.OPEN) {
                        clearInterval(interval)
                        resolve()
                    }
                    currentAttempt++
                }, intervalTime)
            })
        }
        
        const sendMessage = async (socket, msg) => {
            if (socket.readyState !== socket.OPEN) {
                try {
                    await waitForOpenConnection(socket)
                    socket.send(msg)
                } catch (err) { console.error(err) }
            } else {
                socket.send(msg)
            }
        }
        
        return new Promise(function (resolve) {
            self._waitingResponse = self._waitingCancel;
        });
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(...arguments);
        $(window).on('beforeunload', function(){
            paymentSocket.close();
        });


        console.log("--------------------------------------------\n" +
        "REALIZANDO LA ACCION DE CANCELACON SMARTCASH\n" +
        "--------------------------------------------");
        var line = this.pos.get_order().selected_paymentline;
        var order = this.pos.get_order();
        var data = this._terminal_pay_data();
        var Recript_no = this.pos.get_order().name;
        var Login_user = this.pos.get_cashier().name;
        var Pos_name = this.pos.config.name;
        var Gateway_ip = this.pos.config.gateway_ip;
        var Port_ip = this.pos.config.port_ip;

        var dataTime = this._current_time_date();
        var price = parseInt(data.RequestedAmount*100);
        var mensaje = 'DATA;' + data.OrderID +'-'+ dataTime + ';' + Login_user  + ';' + Pos_name + ';' + price + ';' + 1 + ';' + 1;
        
        console.log('Precio: ' + price);
        console.log('Cadenass: ' + mensaje);
        var success = false;
        cancel = true;

        console.log("CONECTANDO A LA IPs: " , Gateway_ip);
        console.log("APUNTANDO AL PUERTO: ", Port_ip);
        var cancelSocket = new WebSocket ("wss://"+Gateway_ip+":"+Port_ip+"");
        

        cancelSocket.onopen = function (event) {
            cancelSocket.send(mensaje);
            console.log("---------------------------------");	
            console.log("SE ENVIA LA CANCELACION A IMACASH");
            console.log("---------------------------------");
        }

        cancelSocket.onmessage = function (event) {

            console.log("ONMESSAGE DE CANCELAR");
            var reader = new FileReader();

            reader.addEventListener("loadend", function() {
                console.log("LISENER DE CANCELAR");
                var recieved = reader.result;
                console.log("Reader.result: " , recieved);
                var code = recieved.substr(recieved.length - 3);
                console.log("Code: ", code);

                if (code == '001') {
                    success = true;
                    paymentSocket.close();          
                }
                
                if(success){
                    // You can send your request from here to the terminal, and based on the response from your
                    // terminal you can set payment_status to success / retry / waiting.
                    console.log("retry");
                    line.set_payment_status('retry');
                    cancelSocket.close();
            
            
                }else{
                    line.set_payment_status('waiting');
                }

                cancelSocket.onerror = function (event) {
                    console.log(event);
                };
    
                cancelSocket.onclose = function (event) {
                    console.log(event);
                    console.log("CERRANDO SOCKET Cancelar");;
                    //line.set_payment_status('retry');
                };
                reader.abort();
            });

            reader.readAsText(event.data);
        };
        
        return new Promise (function (resolver) {
            self._waitingResponse = self.waitingCancel;
        });
    }


    send_payment_reversal() {
        super.send_payment_reversal(...arguments);
        this._super.apply(this, arguments);
    }

    close() {
    console.log("Close");
        this._super.apply(this, arguments);
    }

    _terminal_pay_data() {
        var order = this.pos.get_order();
        var line = order.selected_paymentline;
        var data = {
            'Name': order.name,
            'OrderID': order.uid,
            'TimeStamp': this._current_time_date(),
            'Currency': this.pos.currency.name,
            'RequestedAmount': line.amount,
            'PaymentMethod': this.payment_method
        };
        return data;
    }

    _current_time_date(){
        var currentDate = new Date();
        var month = currentDate.getMonth();
        month = month+1;
        var dataTime = currentDate.getDate() + '/' + month + '/' + currentDate.getFullYear() + '-' + currentDate.getHours() + ':' +
                currentDate.getMinutes() + ':' + currentDate.getSeconds();
        return dataTime;
    }
}
