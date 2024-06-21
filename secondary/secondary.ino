#include <lvgl.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>

#define XPT2046_IRQ 36
#define XPT2046_MOSI 32
#define XPT2046_MISO 39
#define XPT2046_CLK 25
#define XPT2046_CS 33

LV_FONT_DECLARE(noto_sansjp_medium_14_2bpp);

SPIClass mySpi = SPIClass(VSPI);
XPT2046_Touchscreen ts(XPT2046_CS, XPT2046_IRQ);
uint16_t touchScreenMinimumX = 200, touchScreenMaximumX = 3700, touchScreenMinimumY = 240, touchScreenMaximumY = 3800;

/* Change to your screen resolution */
static const uint16_t screenWidth = 320;
static const uint16_t screenHeight = 240;

static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[screenWidth * screenHeight / 10];

TFT_eSPI tft = TFT_eSPI(screenWidth, screenHeight); /* TFT instance */

#if LV_USE_LOG != 0
/* Serial debugging */
void my_print(const char * buf){
    Serial.printf(buf);
    Serial.flush();
}
#endif

/* Display flushing */
void my_disp_flush(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors((uint16_t *)&color_p->full, w * h, true);
    tft.endWrite();

    lv_disp_flush_ready(disp_drv);
}

/* Read the touchpad */
void my_touchpad_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data) {
    if(ts.touched())
    {
        TS_Point p = ts.getPoint();
        // Some very basic auto calibration so it doesn't go out of range
        if(p.x < touchScreenMinimumX) touchScreenMinimumX = p.x;
        if(p.x > touchScreenMaximumX) touchScreenMaximumX = p.x;
        if(p.y < touchScreenMinimumY) touchScreenMinimumY = p.y;
        if(p.y > touchScreenMaximumY) touchScreenMaximumY = p.y;
        // Map this to the pixel position
        data->point.x = map(p.x, touchScreenMinimumX, touchScreenMaximumX, 1, screenWidth); /* Touchscreen X calibration */
        data->point.y = map(p.y, touchScreenMinimumY, touchScreenMaximumY, 1, screenHeight); /* Touchscreen Y calibration */
        data->state = LV_INDEV_STATE_PR;
    }
    else
    {
        data->state = LV_INDEV_STATE_REL;
    }
}

static lv_obj_t * cont;
static lv_obj_t * btn1;


static void event_handler(lv_event_t * e) {
    /* Reset function: clear all labels */
    lv_obj_clean(cont);
}

void lv_btn_reset(void) {
    lv_obj_t * label;

    // Create the button and align it to the bottom-right corner of the screen
    btn1 = lv_btn_create(lv_scr_act());
    lv_obj_add_event_cb(btn1, event_handler, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn1, LV_ALIGN_BOTTOM_RIGHT, -10, -10);

    label = lv_label_create(btn1);
    lv_label_set_text(label, "Reset");
    lv_obj_center(label);
}

void lv_label_log(const char * log) {
    /* Create a container with flex layout if it does not exist */
    if (!cont) {
        cont = lv_obj_create(lv_scr_act());
        lv_obj_set_size(cont, 320, 240); // Set the size to cover the entire screen
        lv_obj_center(cont);
        lv_obj_set_layout(cont, LV_LAYOUT_FLEX);
        lv_obj_set_flex_flow(cont, LV_FLEX_FLOW_COLUMN); // Set flex flow to column

        /* Enable scrolling for the container */
        lv_obj_set_scrollbar_mode(cont, LV_SCROLLBAR_MODE_AUTO);

        /* Remove the border and background color from the container */
        lv_obj_set_style_border_width(cont, 0, 0);
        lv_obj_set_style_bg_opa(cont, LV_OPA_TRANSP, 0);
    }

    lv_obj_t * label = lv_label_create(cont);
    lv_label_set_long_mode(label, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(label, 300);
    lv_label_set_recolor(label, true);
    lv_label_set_text(label, log);
    lv_obj_set_style_translate_x(label, -10, 0);
    lv_obj_set_style_text_font(label, &noto_sansjp_medium_14_2bpp, 0);

    // Adjust the padding to reduce the vertical spacing
    lv_obj_set_style_pad_top(label, -5, 0);    // Adjust top padding
    lv_obj_set_style_pad_bottom(label, -5, 0); // Adjust bottom padding


    // Move the reset button to the foreground
    lv_obj_move_foreground(btn1);

    // Scroll to the bottom to show the newest message
    lv_obj_scroll_to_view(label, LV_ANIM_ON);
}

void process_serial_input(const String & input) {
    int first_bracket_end = input.indexOf(']');
    int second_bracket_start = input.indexOf('[', first_bracket_end);
    int second_bracket_end = input.indexOf(']', second_bracket_start);

    String timestamp = input.substring(1, first_bracket_end);
    String type = input.substring(second_bracket_start + 1, second_bracket_end);
    String message = input.substring(second_bracket_end + 2);

    // デバッグ用のシリアル出力
    Serial.print("Timestamp: ");
    Serial.println(timestamp);
    Serial.print("Type: ");
    Serial.println(type);
    Serial.print("Message: ");
    Serial.println(message);

    String formatted_message = "[" + timestamp.substring(11, 16) + "] ";
    if (type == "Join") {
        formatted_message += "#00ff00 [Join]# " + message;
    } else if (type == "Left") {
        formatted_message += "#ff0000 [Left]# " + message;
    } else if (type == "Serial") {
        formatted_message += "#1e90ff [Serial]# " + message;
    }

    Serial.println(formatted_message); // formatted_messageをシリアルに出力

    lv_label_log(formatted_message.c_str());
}

void setup() {
    Serial.begin(115200); /* prepare for possible serial debug */

    String LVGL_Arduino = "LVGL version ";
    LVGL_Arduino += String('V') + lv_version_major() + "." + lv_version_minor() + "." + lv_version_patch();

    Serial.println(LVGL_Arduino);

    lv_init();

#if LV_USE_LOG != 0
    lv_log_register_print_cb(my_print); /* register print function for debugging */
#endif

    mySpi.begin(XPT2046_CLK, XPT2046_MISO, XPT2046_MOSI, XPT2046_CS); /* Start second SPI bus for touchscreen */
    ts.begin(mySpi); /* Touchscreen init */
    ts.setRotation(1); /* Landscape orientation */

    tft.begin();          /* TFT init */
    tft.setRotation(1); /* Landscape orientation */

    lv_disp_draw_buf_init(&draw_buf, buf, NULL, screenWidth * screenHeight / 10);

    /* Initialize the display */
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    /* Change the following line to your display resolution */
    disp_drv.hor_res = screenWidth;
    disp_drv.ver_res = screenHeight;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    /* Initialize the (dummy) input device driver */
    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = my_touchpad_read;
    lv_indev_t * my_indev = lv_indev_drv_register(&indev_drv);

    // Create reset button
    lv_btn_reset();
    
    Serial.println("Setup done");
}

void loop() {
    lv_timer_handler(); /* let the GUI do its work */
    delay(5);

    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        process_serial_input(input);
    }
}
