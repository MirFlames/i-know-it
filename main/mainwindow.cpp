#include "mainwindow.h"
#include "auth.h"
#include "ui_mainwindow.h"
#include <QTextCharFormat>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::About_Lab1()
{
    auth *dg = new auth();
    dg->show();
}


void MainWindow::on_comboBox_currentIndexChanged(int index)
{
    ui->calendarWidget->setFirstDayOfWeek(Qt::DayOfWeek(index+1));
    QTextCharFormat format;
    format.setForeground(qvariant_cast<QColor>("green"));
    QTextCharFormat default_color;
    default_color.setForeground(qvariant_cast<QColor>("black"));
    for (int day = 1; day <= 7; day++)
    {
        ui->calendarWidget->setWeekdayTextFormat(Qt::DayOfWeek(day), (day == index+1?format:default_color));
    }
}
