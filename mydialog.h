#ifndef MYDIALOG_H
#define MYDIALOG_H

#include <QDialog>
#include <QFile>
#include<QIODevice>
#include<QTextStream>
#include <QSpinBox>
#include <QTextEdit>
#include <QHBoxLayout>
#include <QComboBox>
#include <QPushButton>
#include <QFileDialog>
#include <QSaveFile>
#include <QMessageBox>

QT_BEGIN_NAMESPACE
namespace Ui { class MyDialog; }
QT_END_NAMESPACE

class MyDialog : public QDialog
{
    Q_OBJECT

public:
    MyDialog(QWidget *parent = nullptr);
    ~MyDialog();

private:
    Ui::MyDialog *ui;
    QSpinBox *sBox = new QSpinBox;
    QTextEdit *tEdit = new QTextEdit;
    QHBoxLayout *Hlay = new QHBoxLayout;
    QComboBox *cBox = new QComboBox;
    QPushButton *But = new QPushButton;

private slots:
    void  Wrf();
};
#endif // MYDIALOG_H
