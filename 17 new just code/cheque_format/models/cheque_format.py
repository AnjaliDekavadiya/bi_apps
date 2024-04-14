# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class ChequeFormat(models.Model):
    _name = 'cheque.format'
    _description = "Create Cheque Format"

    name = fields.Char(string="Cheque Name", required=True)
    ac_pay_margin_top = fields.Char()
    ac_pay_margin_left = fields.Char()
    ac_pay_letter_space = fields.Char()
    ac_pay_rotate = fields.Char(string='Rotation Text')
    ac_pay_css = fields.Char(string='Letter Spacing(ac_pay)')
    font_size = fields.Char(string="Font Size", default="20")
    font_css = fields.Char()
    ben_margin_top = fields.Char()
    ben_margin_left = fields.Char()
    beneficiary_css = fields.Char()
    date_margin_top = fields.Char(string='Top Margin')
    date_margin_left = fields.Char(string='Left Margin')
    date_letter_space = fields.Char(string='Letter Spacing')
    date_css = fields.Char()
    amount_digit_top = fields.Char()
    amount_digit_left = fields.Char()
    amount_digit_letter_space = fields.Char()
    amount_digit_css = fields.Char()
    amount_word_top = fields.Char()
    amount_word_left = fields.Char()
    amount_word_letter_space = fields.Char()
    amount_word_css = fields.Char()

    @api.onchange(
        'ac_pay_margin_top', 'ac_pay_margin_left', 'ac_pay_letter_space',
        'ac_pay_rotate', 'font_size', 'ben_margin_top', 'ben_margin_left', 'date_margin_top',
        'date_margin_left', 'date_letter_space', 'amount_digit_top', 'amount_digit_left',
        'amount_digit_letter_space', 'amount_word_top', 'amount_word_left', 'amount_word_letter_space')
    def _compute_config(self):
        ac_pay_css = beneficiary_css = date_css = amount_digit_css = amount_word_css = ''
        if self.font_size:
            self.font_css = 'font-size:' + self.font_size + 'px;'

        if self.ac_pay_margin_top:
            ac_pay_css += 'margin-top:' + self.ac_pay_margin_top + 'px;'
        if self.ac_pay_margin_left:
            ac_pay_css += 'margin-left:' + self.ac_pay_margin_left + 'px;'
        if self.ac_pay_letter_space:
            ac_pay_css += 'letter-spacing:' + self.ac_pay_letter_space + 'px;'
        if self.ac_pay_rotate:
            ac_pay_css += 'transform: rotate(' + self.ac_pay_rotate + 'deg);-webkit-transform:rotate(' + self.ac_pay_rotate + 'deg);'
        self.ac_pay_css = ac_pay_css

        if self.ben_margin_top:
            beneficiary_css += 'margin-top:' + self.ben_margin_top + 'px;'
        if self.ben_margin_left:
            beneficiary_css += 'margin-left:' + self.ben_margin_left + 'px;'
        self.beneficiary_css = beneficiary_css

        if self.date_margin_top:
            date_css += 'margin-top:' + self.date_margin_top + 'px;'
        if self.date_margin_left:
            date_css += 'margin-left:' + self.date_margin_left + 'px;'
        if self.date_letter_space:
            date_css += 'letter-spacing:' + self.date_letter_space + 'px;'
        self.date_css = date_css

        if self.amount_digit_top:
            amount_digit_css += 'margin-top:' + self.amount_digit_top + 'px;'
        if self.amount_digit_left:
            amount_digit_css += 'margin-left:' + self.amount_digit_left + 'px;'
        if self.amount_digit_letter_space:
            amount_digit_css += 'letter-spacing:' + self.amount_digit_letter_space + 'px;'
        self.amount_digit_css = amount_digit_css

        if self.amount_word_top:
            amount_word_css += 'margin-top:' + self.amount_word_top + 'px;'
        if self.amount_word_left:
            amount_word_css += 'margin-left:' + self.amount_word_left + 'px;'
        if self.amount_word_letter_space:
            amount_word_css += 'letter-spacing:' + self.amount_word_letter_space + 'px;'
        self.amount_word_css = amount_word_css


class account_payment(models.Model):
    _inherit = "account.payment"

    cheque_format = fields.Many2one('cheque.format', string="Cheque Format")
