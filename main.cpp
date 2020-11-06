#include "mydialog.h"

#include <QApplication>
#include <QSpinBox>
#include <QTextEdit>
#include <QHBoxLayout>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MyDialog dg;
    dg.show();
    return a.exec();
}
